"""Compatibility entry points backed exclusively by IAM V4.

The public function name is retained to limit churn in older business modules;
it no longer constructs or calls ``iam.IAM`` / the IAM V3 API client.
"""

from django.db.models import Q

from gcloud.iam_auth.apply_service import ApplyService, checks_from_permission_payload
from gcloud.iam_auth.conf import ACTION_RESOURCE_TYPES
from gcloud.iam_auth.exceptions import IAMPermissionDenied, IAMResourceNotFound, IAMV4ProtocolError
from gcloud.iam_auth.scope_resolver import ScopeResolver
from gcloud.iam_auth.service import PermissionService
from gcloud.iam_auth.types import PermissionCheck


def _single_resource(resources):
    resources = resources or []
    if len(resources) > 1:
        raise IAMV4ProtocolError("a V4 direct-auth check accepts at most one resource")
    return resources[0] if resources else None


def _resource_for_action(action_id, resources):
    resource = _single_resource(resources)
    expected_type = ACTION_RESOURCE_TYPES.get(action_id)
    if action_id in ACTION_RESOURCE_TYPES and expected_type is not None and resource is None:
        raise IAMResourceNotFound(expected_type, "unknown")
    return resource


class IAMV4PermissionAdapter:
    def __init__(self, tenant_id):
        self.tenant_id = tenant_id
        self.service = PermissionService()

    def _identity(self, subject):
        if not self.tenant_id:
            raise IAMV4ProtocolError("tenant_id is required")
        return subject.id, self.tenant_id

    def is_allowed(self, request):
        username, tenant_id = self._identity(request.subject)
        resources = request.resources or []
        if len(resources) <= 1:
            return self.service.is_allowed(
                username,
                tenant_id,
                PermissionCheck(request.action.id, _resource_for_action(request.action.id, resources)),
            )
        decisions = self.service.allowed_resources(username, tenant_id, request.action.id, resources)
        return all(decisions.values())

    def is_allowed_with_cache(self, request):
        return self.is_allowed(request)

    def batch_is_allowed(self, request, resources_list):
        username, tenant_id = self._identity(request.subject)
        resources = [_single_resource(item) for item in resources_list]
        return self.service.allowed_resources(username, tenant_id, request.action.id, resources)

    def batch_resource_multi_actions_allowed(self, request, resources_list):
        username, tenant_id = self._identity(request.subject)
        resources = [_single_resource(item) for item in resources_list]
        return self.service.allowed_resource_actions(
            username, tenant_id, [action.id for action in request.actions], resources
        )

    def resource_multi_actions_allowed(self, request):
        username, tenant_id = self._identity(request.subject)
        return self.service.allowed_actions(
            username,
            tenant_id,
            [action.id for action in request.actions],
            _single_resource(request.resources),
        )

    def make_filter(self, request, key_mapping):
        username, tenant_id = self._identity(request.subject)
        resource_type = ACTION_RESOURCE_TYPES.get(request.action.id)
        if not resource_type:
            raise IAMV4ProtocolError("authorized scope requires a resource action")
        orm_field = key_mapping.get("{}.id".format(resource_type))
        if not orm_field:
            raise IAMV4ProtocolError("authorized scope key mapping is missing")
        scope = ScopeResolver().authorized_scope(username, tenant_id, request.action.id)
        queryset = scope.queryset(resource_type)
        ids = queryset.values("id") if queryset is not None else scope.ids(resource_type)
        return Q(**{"{}__in".format(orm_field): ids})

    def get_apply_url(self, application):
        """Rebuild every resource and ancestor from the tenant database."""

        checks = checks_from_permission_payload(application, self.tenant_id)
        url = ApplyService().generate_url(self.tenant_id, checks)
        return True, "", url


def get_iam_client(tenant_id):
    return IAMV4PermissionAdapter(tenant_id)


def allow_or_raise_auth_failed(iam, system, subject, action, resources, cache=False):
    check = PermissionCheck(action.id, _resource_for_action(action.id, resources))
    if not iam.service.is_allowed(subject.id, iam.tenant_id, check):
        raise IAMPermissionDenied([check])
