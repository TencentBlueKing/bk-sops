from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin

from gcloud.iam_auth.exceptions import (
    AuthFailedException,
    IAMPermissionDenied,
    IAMResourceNotFound,
    IAMV4ProtocolError,
    IAMV4Unavailable,
    MultiAuthFailedException,
    RawAuthFailedException,
)
from gcloud.iam_auth.presentation import serialize_missing_permissions


def get_request_id(request, exception=None):
    return (
        getattr(exception, "request_id", "")
        or getattr(request, "trace_id", "")
        or request.META.get("HTTP_X_REQUEST_ID", "")
    )


class IAMPermissionDeniedMiddleware(MiddlewareMixin):
    def process_exception(self, request, exception):
        if isinstance(exception, IAMResourceNotFound):
            return JsonResponse(
                {
                    "result": False,
                    "code": "RESOURCE_NOT_FOUND",
                    "message": "resource not found",
                    "request_id": get_request_id(request, exception),
                },
                status=404,
            )
        if isinstance(exception, IAMPermissionDenied):
            return JsonResponse(
                {
                    "result": False,
                    "code": 499,
                    "message": "permission denied",
                    "permission": serialize_missing_permissions(exception.missing_permissions),
                    "request_id": get_request_id(request, exception),
                },
                status=499,
            )
        if isinstance(exception, (AuthFailedException, MultiAuthFailedException, RawAuthFailedException)):
            return JsonResponse(
                {
                    "result": False,
                    "code": 499,
                    "message": "permission denied",
                    "permission": exception.perms_apply_data(),
                    "request_id": get_request_id(request, exception),
                },
                status=499,
            )
        if isinstance(exception, (IAMV4Unavailable, IAMV4ProtocolError)):
            return JsonResponse(
                {
                    "result": False,
                    "code": "IAM_V4_UNAVAILABLE",
                    "message": "IAM service unavailable",
                    "request_id": get_request_id(request, exception),
                },
                status=503,
            )
        return None
