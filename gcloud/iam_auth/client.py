import logging

from bk_resource.exceptions import APIRequestError
from django.conf import settings

from gcloud.iam_auth.api_v4.resources import (
    DirectAuthByActionsResource,
    DirectAuthByResourcesResource,
    DirectAuthResource,
    ListAuthorizedResourceResource,
    RetrieveCallbackTokenResource,
)
from gcloud.iam_auth.conf import ACTION_RESOURCE_TYPES, RESOURCE_TYPE_IDS, RESOURCES_BY_ID
from gcloud.iam_auth.exceptions import IAMV4Error, IAMV4ProtocolError, IAMV4Unavailable
from gcloud.iam_auth.payloads import resource_to_v4_auth

logger = logging.getLogger(__name__)


def _chunks(items, chunk_size):
    for index in range(0, len(items), chunk_size):
        yield items[index : index + chunk_size]


def _api_request(resource, payload, allow_not_found=False):
    try:
        return resource.request(payload)
    except IAMV4Error:
        raise
    except APIRequestError as error:
        data = getattr(error, "data", {})
        status_code = getattr(error, "status_code", None)
        if status_code is None and isinstance(data, dict):
            status_code = data.get("status_code")
        error_code = data.get("code") if isinstance(data, dict) else None
        error_message = data.get("message") if isinstance(data, dict) else None
        request_id = data.get("request_id", "") if isinstance(data, dict) else ""
        logger.error(
            "IAM V4 gateway request failed: resource=%s method=%s action=%s status_code=%s "
            "error_code=%s error_message=%s request_id=%s",
            getattr(resource, "name", resource.__class__.__name__),
            getattr(resource, "method", ""),
            getattr(resource, "action", ""),
            status_code,
            error_code,
            error_message,
            request_id,
        )
        if allow_not_found and status_code == 404:
            return None
        raise IAMV4Unavailable(request_id=request_id) from error
    except Exception as error:
        logger.exception(
            "IAM V4 gateway transport failed: resource=%s method=%s action=%s",
            getattr(resource, "name", resource.__class__.__name__),
            getattr(resource, "method", ""),
            getattr(resource, "action", ""),
        )
        raise IAMV4Unavailable() from error


def validate_action_decisions(data, requested_action_ids):
    requested = list(requested_action_ids)
    if len(requested) != len(set(requested)):
        raise IAMV4ProtocolError("duplicate requested action id")
    if not isinstance(data, list):
        raise IAMV4ProtocolError("auth-by-actions data must be a list")

    decisions = {}
    for row in data:
        if not isinstance(row, dict):
            raise IAMV4ProtocolError("auth-by-actions row must be an object")
        action_id = row.get("action_id")
        allowed = row.get("allowed")
        if action_id not in requested or action_id in decisions or not isinstance(allowed, bool):
            raise IAMV4ProtocolError("invalid auth-by-actions decision")
        decisions[action_id] = allowed
    if set(decisions) != set(requested):
        raise IAMV4ProtocolError("auth-by-actions response is incomplete")
    return {action_id: decisions[action_id] for action_id in requested}


def validate_resource_decisions(data, requested_resources):
    requested = [str(resource.id) for resource in requested_resources]
    if len(requested) != len(set(requested)):
        raise IAMV4ProtocolError("duplicate requested resource id")
    if not isinstance(data, list):
        raise IAMV4ProtocolError("auth-by-resources data must be a list")

    decisions = {}
    for row in data:
        if not isinstance(row, dict):
            raise IAMV4ProtocolError("auth-by-resources row must be an object")
        resource_id = row.get("resource_id")
        allowed = row.get("allowed")
        if not isinstance(resource_id, str):
            raise IAMV4ProtocolError("resource_id must be a string")
        if resource_id not in requested or resource_id in decisions or not isinstance(allowed, bool):
            raise IAMV4ProtocolError("invalid auth-by-resources decision")
        decisions[resource_id] = allowed
    if set(decisions) != set(requested):
        raise IAMV4ProtocolError("auth-by-resources response is incomplete")
    return {resource_id: decisions[resource_id] for resource_id in requested}


def _scope_resource_types(resource_type):
    allowed = set()
    current = resource_type
    while current:
        if current in allowed or current not in RESOURCES_BY_ID:
            raise IAMV4ProtocolError("resource topology is invalid")
        allowed.add(current)
        current = RESOURCES_BY_ID[current]["parent_id"]
    return allowed


def validate_authorized_resources(data, expected_resource_type=None):
    if not isinstance(data, list):
        raise IAMV4ProtocolError("authorized-resources data must be a list")

    rows = []
    seen_types = set()
    for row in data:
        if not isinstance(row, dict):
            raise IAMV4ProtocolError("authorized-resources row must be an object")
        resource_type = row.get("type")
        ids = row.get("ids")
        if resource_type not in RESOURCE_TYPE_IDS or resource_type in seen_types:
            raise IAMV4ProtocolError("authorized-resources contains an invalid resource type")
        if expected_resource_type is not None and resource_type not in _scope_resource_types(expected_resource_type):
            raise IAMV4ProtocolError("authorized-resources returned an unexpected resource type")
        if not isinstance(ids, list) or any(not isinstance(item, str) or not item for item in ids):
            raise IAMV4ProtocolError("authorized-resources ids must be non-empty strings")
        ids = list(dict.fromkeys(ids))
        if "*" in ids:
            ids = ["*"]
        seen_types.add(resource_type)
        rows.append({"type": resource_type, "ids": ids})
    return rows


class IAMV4Client:
    def __init__(self, system_id=None, chunk_size=None):
        self.system_id = system_id or settings.BK_IAM_SYSTEM_ID
        self.chunk_size = settings.IAM_V4_BATCH_AUTH_CHUNK_SIZE if chunk_size is None else chunk_size
        if not isinstance(self.chunk_size, int) or not 1 <= self.chunk_size <= 20:
            raise IAMV4ProtocolError("IAM V4 batch auth chunk size must be between 1 and 20")

    @staticmethod
    def _subject_payload(subject):
        return {"type": subject.type, "id": str(subject.id)}

    def direct_auth(self, tenant_id, subject, action_id, resource=None):
        payload = {
            "tenant_id": tenant_id,
            "system_id": self.system_id,
            "subject": self._subject_payload(subject),
            "action_id": action_id,
        }
        if resource is not None:
            payload["resource"] = resource_to_v4_auth(resource)
        data = _api_request(DirectAuthResource(), payload)
        allowed = data.get("allowed") if isinstance(data, dict) else None
        if not isinstance(allowed, bool):
            raise IAMV4ProtocolError("direct auth response missing boolean data.allowed")
        return allowed

    def direct_auth_by_actions(self, tenant_id, subject, action_ids, resource=None):
        action_ids = list(action_ids)
        if not action_ids:
            return {}
        result = {}
        for action_chunk in _chunks(action_ids, self.chunk_size):
            payload = {
                "tenant_id": tenant_id,
                "system_id": self.system_id,
                "subject": self._subject_payload(subject),
                "action_ids": action_chunk,
            }
            if resource is not None:
                payload["resource"] = resource_to_v4_auth(resource)
            data = _api_request(DirectAuthByActionsResource(), payload)
            result.update(validate_action_decisions(data, action_chunk))
        return {action_id: result[action_id] for action_id in action_ids}

    def direct_auth_by_resources(self, tenant_id, subject, action_id, resources):
        resources = list(resources)
        if not resources:
            return {}
        result = {}
        for resource_chunk in _chunks(resources, self.chunk_size):
            data = _api_request(
                DirectAuthByResourcesResource(),
                {
                    "tenant_id": tenant_id,
                    "system_id": self.system_id,
                    "subject": self._subject_payload(subject),
                    "action_id": action_id,
                    "resources": [resource_to_v4_auth(resource) for resource in resource_chunk],
                },
            )
            result.update(validate_resource_decisions(data, resource_chunk))
        return {str(resource.id): result[str(resource.id)] for resource in resources}

    def list_authorized_resources(self, tenant_id, subject, action_id):
        expected_resource_type = ACTION_RESOURCE_TYPES.get(action_id)
        if action_id not in ACTION_RESOURCE_TYPES or expected_resource_type is None:
            raise IAMV4ProtocolError("authorized scope requires a resource action")
        data = _api_request(
            ListAuthorizedResourceResource(),
            {
                "tenant_id": tenant_id,
                "system_id": self.system_id,
                "subject": self._subject_payload(subject),
                "action_id": action_id,
            },
        )
        return validate_authorized_resources(data, expected_resource_type)

    def retrieve_callback_token(self, tenant_id):
        data = _api_request(
            RetrieveCallbackTokenResource(),
            {"tenant_id": tenant_id, "system_id": self.system_id},
        )
        token = data.get("auth_token") if isinstance(data, dict) else None
        if not isinstance(token, str) or not token:
            raise IAMV4ProtocolError("callback token response missing data.auth_token")
        return token
