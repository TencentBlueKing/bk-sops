import json
import logging

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.exceptions import ValidationError

from gcloud.iam_auth.exceptions import IAMV4Error
from gcloud.iam_auth.resource_api_v4.auth import CallbackTenantMissing, CallbackUnauthorized, authenticate_callback
from gcloud.iam_auth.resource_api_v4.providers import PROVIDERS
from gcloud.iam_auth.resource_api_v4.serializers import CallbackRequestSerializer

logger = logging.getLogger("root")


def _response(request_id, data=None, error=None, status=200):
    body = {"data": data} if error is None else {"error": error}
    response = JsonResponse(body, status=status)
    response["X-Request-Id"] = request_id
    return response


def _error(request_id, code, message, status):
    return _response(request_id, error={"code": code, "message": message}, status=status)


@csrf_exempt
def resource_callback(request):
    request_id = request.META.get("HTTP_X_REQUEST_ID", "")
    if request.method != "POST":
        return _error(request_id, "METHOD_NOT_ALLOWED", "only POST is allowed", 405)
    try:
        tenant_id = authenticate_callback(request)
    except CallbackTenantMissing:
        return _error(request_id, "TENANT_REQUIRED", "tenant header is required", 400)
    except CallbackUnauthorized:
        logger.warning("IAM V4 callback authentication failed, request_id=%s", request_id)
        return _error(request_id, "UNAUTHORIZED", "basic authentication failed", 401)
    except IAMV4Error:
        logger.error("IAM V4 callback token service failed, request_id=%s", request_id)
        return _error(request_id, "IAM_UNAVAILABLE", "IAM service unavailable", 503)

    try:
        payload = json.loads(request.body)
        serializer = CallbackRequestSerializer(data=payload)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        provider = PROVIDERS[data["type"]]
        if data["method"] == "list_instance":
            filter_data = data.get("filter", {})
            result = provider.list_instance(
                tenant_id,
                parent=filter_data.get("parent"),
                keyword=filter_data.get("keyword", ""),
                **data["page"],
            )
        else:
            result = provider.fetch_instance_info(
                tenant_id,
                ids=data["filter"]["ids"],
                requires=data.get("requires", ()),
            )
    except ValidationError as error:
        logger.warning(
            "IAM V4 callback request validation failed, type=%s method=%s errors=%s request_id=%s",
            payload.get("type") if isinstance(payload, dict) else "",
            payload.get("method") if isinstance(payload, dict) else "",
            error.detail,
            request_id,
        )
        return _error(request_id, "INVALID_REQUEST", str(error), 400)
    except (ValueError, TypeError) as error:
        logger.warning(
            "IAM V4 callback request parsing failed, error_type=%s request_id=%s",
            type(error).__name__,
            request_id,
        )
        return _error(request_id, "INVALID_REQUEST", str(error), 400)
    except IAMV4Error as error:
        return _error(request_id, "INVALID_REQUEST", str(error), 422)
    except Exception:
        logger.exception("IAM V4 callback failed, request_id=%s", request_id)
        return _error(request_id, "INTERNAL_ERROR", "resource callback failed", 500)
    return _response(request_id, data=result)
