from gcloud.iam_auth.client import IAMV4Client
from gcloud.iam_auth.conf import ACTION_RESOURCE_TYPES
from gcloud.iam_auth.creator import creator_action_allowed
from gcloud.iam_auth.exceptions import IAMPermissionDenied, IAMResourceNotFound, IAMV4ProtocolError
from gcloud.iam_auth.models import Subject
from gcloud.iam_auth.repository import local_resource_queryset
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
    validate_local_resources([check.resource] if check.resource is not None else [], tenant_id)


def validate_local_resources(resources, tenant_id):
    resources_by_type = {}
    for resource in resources:
        resources_by_type.setdefault(resource.type, set()).add(str(resource.id))
    for resource_type, expected_ids in resources_by_type.items():
        existing_ids = {
            str(item)
            for item in local_resource_queryset(resource_type, tenant_id)
            .filter(id__in=expected_ids)
            .values_list("id", flat=True)
        }
        missing_ids = expected_ids - existing_ids
        if missing_ids:
            raise IAMResourceNotFound(resource_type, sorted(missing_ids)[0])


def validate_checks(checks, tenant_id):
    checks = list(checks)
    for check in checks:
        validate_check(check)
    validate_local_resources([check.resource for check in checks if check.resource is not None], tenant_id)
    return checks


class PermissionService:
    def __init__(self, client=None):
        self.client = client or IAMV4Client()

    def is_allowed(self, username, tenant_id, check):
        validate_identity(username, tenant_id)
        validate_checks([check], tenant_id)
        return self._is_allowed_validated(username, tenant_id, check)

    def _is_allowed_validated(self, username, tenant_id, check):
        if creator_action_allowed(username, check.action_id, check.resource):
            return True
        subject = Subject("user", username)
        return self.client.direct_auth(tenant_id, subject, check.action_id, check.resource)

    def require(self, username, tenant_id, check):
        if not self.is_allowed(username, tenant_id, check):
            raise IAMPermissionDenied([check])

    def require_all(self, username, tenant_id, checks):
        validate_identity(username, tenant_id)
        checks = validate_checks(checks, tenant_id)
        missing = [check for check in checks if not self._is_allowed_validated(username, tenant_id, check)]
        if missing:
            raise IAMPermissionDenied(missing)

    def allowed_actions(self, username, tenant_id, action_ids, resource=None):
        validate_identity(username, tenant_id)
        action_ids = list(action_ids)
        validate_checks([PermissionCheck(action_id, resource) for action_id in action_ids], tenant_id)
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
        validate_checks([PermissionCheck(action_id, resource) for resource in resources], tenant_id)
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

    def allowed_resource_actions(self, username, tenant_id, action_ids, resources):
        """Authorize a resource/action matrix after one tenant-local validation pass."""
        validate_identity(username, tenant_id)
        action_ids = list(action_ids)
        resources = list(resources)
        for action_id in action_ids:
            for resource in resources:
                validate_check(PermissionCheck(action_id, resource))
        validate_local_resources(resources, tenant_id)
        result = {str(resource.id): {} for resource in resources}
        subject = Subject("user", username)
        for action_id in action_ids:
            creator_ids = {
                str(resource.id) for resource in resources if creator_action_allowed(username, action_id, resource)
            }
            remote_resources = [resource for resource in resources if str(resource.id) not in creator_ids]
            decisions = (
                self.client.direct_auth_by_resources(tenant_id, subject, action_id, remote_resources)
                if remote_resources
                else {}
            )
            for resource in resources:
                resource_id = str(resource.id)
                result[resource_id][action_id] = resource_id in creator_ids or decisions[resource_id]
        return result

    def require_resources(self, username, tenant_id, action_id, resources):
        resources = list(resources)
        decisions = self.allowed_resources(username, tenant_id, action_id, resources)
        missing = [PermissionCheck(action_id, resource) for resource in resources if not decisions[str(resource.id)]]
        if missing:
            raise IAMPermissionDenied(missing)
