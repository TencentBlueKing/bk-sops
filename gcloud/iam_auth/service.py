from gcloud.iam_auth.client import IAMV4Client
from gcloud.iam_auth.conf import ACTION_RESOURCE_TYPES
from gcloud.iam_auth.creator import creator_action_allowed
from gcloud.iam_auth.exceptions import IAMPermissionDenied, IAMResourceNotFound, IAMV4ProtocolError
from gcloud.iam_auth.models import Subject
from gcloud.iam_auth.repository import resource_exists
from gcloud.iam_auth.types import PermissionCheck


def validate_identity(username, tenant_id):
    if not isinstance(username, str) or not username.strip():
        raise IAMV4ProtocolError("username is required")
    if not isinstance(tenant_id, str) or not tenant_id.strip():
        raise IAMV4ProtocolError("tenant_id is required")


_MISSING = object()


def validate_check(check):
    if not isinstance(check, PermissionCheck):
        raise IAMV4ProtocolError("invalid permission check")
    expected_resource_type = ACTION_RESOURCE_TYPES.get(check.action_id, _MISSING)
    if expected_resource_type is _MISSING:
        raise IAMV4ProtocolError("unknown action id")
    if expected_resource_type is None:
        if check.resource is not None:
            raise IAMV4ProtocolError("system action must not contain a resource")
        return
    if check.resource is None or check.resource.type != expected_resource_type:
        raise IAMV4ProtocolError("action resource type mismatch")
    if not str(check.resource.id):
        raise IAMV4ProtocolError("resource id is required")


def validate_local_resource(check, tenant_id):
    if check.resource is not None and not resource_exists(check.resource.type, check.resource.id, tenant_id):
        raise IAMResourceNotFound(check.resource.type, check.resource.id)


class PermissionService:
    def __init__(self, client=None):
        self.client = client or IAMV4Client()

    def is_allowed(self, username, tenant_id, check):
        validate_identity(username, tenant_id)
        validate_check(check)
        validate_local_resource(check, tenant_id)
        if creator_action_allowed(username, check.action_id, check.resource):
            return True
        subject = Subject("user", username)
        return self.client.direct_auth(tenant_id, subject, check.action_id, check.resource)

    def require(self, username, tenant_id, check):
        if not self.is_allowed(username, tenant_id, check):
            raise IAMPermissionDenied([check])

    def require_all(self, username, tenant_id, checks):
        checks = list(checks)
        missing = [check for check in checks if not self.is_allowed(username, tenant_id, check)]
        if missing:
            raise IAMPermissionDenied(missing)

    def allowed_actions(self, username, tenant_id, action_ids, resource=None):
        validate_identity(username, tenant_id)
        action_ids = list(action_ids)
        for action_id in action_ids:
            check = PermissionCheck(action_id, resource)
            validate_check(check)
            validate_local_resource(check, tenant_id)
        creator_actions = {
            action_id for action_id in action_ids if creator_action_allowed(username, action_id, resource)
        }
        remote_actions = [action_id for action_id in action_ids if action_id not in creator_actions]
        decisions = (
            self.client.direct_auth_by_actions(tenant_id, Subject("user", username), remote_actions, resource)
            if remote_actions
            else {}
        )
        return {action_id: action_id in creator_actions or decisions[action_id] for action_id in action_ids}

    def allowed_resources(self, username, tenant_id, action_id, resources):
        validate_identity(username, tenant_id)
        resources = list(resources)
        for resource in resources:
            check = PermissionCheck(action_id, resource)
            validate_check(check)
            validate_local_resource(check, tenant_id)
        creator_resource_ids = {
            str(resource.id) for resource in resources if creator_action_allowed(username, action_id, resource)
        }
        remote_resources = [resource for resource in resources if str(resource.id) not in creator_resource_ids]
        decisions = (
            self.client.direct_auth_by_resources(tenant_id, Subject("user", username), action_id, remote_resources)
            if remote_resources
            else {}
        )
        return {
            str(resource.id): str(resource.id) in creator_resource_ids or decisions[str(resource.id)]
            for resource in resources
        }

    def require_resources(self, username, tenant_id, action_id, resources):
        resources = list(resources)
        decisions = self.allowed_resources(username, tenant_id, action_id, resources)
        missing = [PermissionCheck(action_id, resource) for resource in resources if not decisions[str(resource.id)]]
        if missing:
            raise IAMPermissionDenied(missing)
