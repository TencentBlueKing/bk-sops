from collections import OrderedDict

from django.conf import settings

from gcloud.iam_auth.api_v4.resources import GenerateApplyURLResource
from gcloud.iam_auth.client import _api_request
from gcloud.iam_auth.conf import ACTION_RESOURCE_TYPES, COMMON_FLOW_PROJECT_ACTION_PAIRS
from gcloud.iam_auth.exceptions import IAMV4ProtocolError
from gcloud.iam_auth.payloads import resource_to_v4_apply
from gcloud.iam_auth.service import validate_check, validate_identity, validate_local_resource
from gcloud.iam_auth.types import PermissionCheck


def _resource_from_id(resource_type, resource_id, tenant_id):
    from gcloud.iam_auth.res_factory import resources_for_type

    resources = resources_for_type(resource_type, resource_id, tenant_id)
    if len(resources) != 1:
        from gcloud.iam_auth.exceptions import IAMResourceNotFound

        raise IAMResourceNotFound(resource_type, resource_id)
    return resources[0]


def checks_from_simple_payload(action_id, resources, tenant_id):
    expected_type = ACTION_RESOURCE_TYPES.get(action_id)
    if action_id not in ACTION_RESOURCE_TYPES:
        raise IAMV4ProtocolError("unknown action id")
    if expected_type is None:
        if resources:
            raise IAMV4ProtocolError("system action must not contain resources")
        return [PermissionCheck(action_id)]
    paired_action_id = COMMON_FLOW_PROJECT_ACTION_PAIRS.get(action_id)
    if paired_action_id:
        paired_actions = (
            (action_id, expected_type),
            (paired_action_id, ACTION_RESOURCE_TYPES[paired_action_id]),
        )
        if not isinstance(resources, list) or len(resources) != len(paired_actions):
            raise IAMV4ProtocolError("paired resource action requires one resource of each type")
        resources_by_type = {}
        for submitted in resources:
            if not isinstance(submitted, dict) or submitted.get("type") in resources_by_type:
                raise IAMV4ProtocolError("paired action resources are invalid")
            resources_by_type[submitted.get("type")] = submitted
        if set(resources_by_type) != {resource_type for _, resource_type in paired_actions}:
            raise IAMV4ProtocolError("action resource type mismatch")
        return [
            PermissionCheck(
                check_action_id,
                _resource_from_id(resource_type, resources_by_type[resource_type].get("id"), tenant_id),
            )
            for check_action_id, resource_type in paired_actions
        ]
    if not isinstance(resources, list) or len(resources) != 1:
        raise IAMV4ProtocolError("resource action requires exactly one resource")
    submitted = resources[0]
    if not isinstance(submitted, dict) or submitted.get("type") != expected_type:
        raise IAMV4ProtocolError("action resource type mismatch")
    return [PermissionCheck(action_id, _resource_from_id(expected_type, submitted.get("id"), tenant_id))]


def checks_from_permission_payload(application, tenant_id):
    if not isinstance(application, dict) or not isinstance(application.get("actions"), list):
        raise IAMV4ProtocolError("permission payload is invalid")
    checks = []
    for action in application["actions"]:
        if not isinstance(action, dict):
            raise IAMV4ProtocolError("permission action is invalid")
        action_id = action.get("id")
        expected_type = ACTION_RESOURCE_TYPES.get(action_id)
        if action_id not in ACTION_RESOURCE_TYPES:
            raise IAMV4ProtocolError("unknown action id")
        related_types = action.get("related_resource_types", [])
        if not isinstance(related_types, list):
            raise IAMV4ProtocolError("related resource types must be a list")
        submitted_resources = []
        for related in related_types:
            if not isinstance(related, dict) or related.get("type") != expected_type:
                raise IAMV4ProtocolError("action resource type mismatch")
            instances = related.get("instances", [])
            if not isinstance(instances, list):
                raise IAMV4ProtocolError("resource instances must be a list")
            for chain in instances:
                if not isinstance(chain, list) or not chain or not isinstance(chain[-1], dict):
                    raise IAMV4ProtocolError("resource instance chain is invalid")
                submitted_resources.append(chain[-1])
        if expected_type is None:
            if submitted_resources:
                raise IAMV4ProtocolError("system action must not contain resources")
            checks.append(PermissionCheck(action_id))
        elif not submitted_resources:
            # IAM V4 permits an apply request without fixed instances; the
            # applicant selects the resource scope on the IAM page.
            checks.append(PermissionCheck(action_id))
        else:
            checks.extend(
                PermissionCheck(action_id, _resource_from_id(expected_type, item.get("id"), tenant_id))
                for item in submitted_resources
            )
    if not checks:
        raise IAMV4ProtocolError("permission payload is empty")
    return checks


class ApplyService:
    def build_permissions(self, checks, tenant_id):
        grouped = OrderedDict()
        seen = set()
        for check in checks:
            if not isinstance(check, PermissionCheck):
                raise IAMV4ProtocolError("invalid permission check")
            expected_type = ACTION_RESOURCE_TYPES.get(check.action_id)
            if check.action_id not in ACTION_RESOURCE_TYPES:
                raise IAMV4ProtocolError("unknown action id")
            if check.resource is not None:
                validate_check(check)
                validate_local_resource(check, tenant_id)
            elif expected_type is None:
                validate_check(check)
            key = (
                check.action_id,
                check.resource.type if check.resource else None,
                str(check.resource.id) if check.resource else None,
            )
            if key in seen:
                continue
            seen.add(key)
            item = grouped.setdefault(check.action_id, {"action_id": check.action_id})
            if check.resource is not None:
                item.setdefault("resources", []).append(resource_to_v4_apply(check.resource))
        permissions = list(grouped.values())
        if not permissions:
            raise IAMV4ProtocolError("at least one permission is required")
        return permissions

    def generate_url(self, tenant_id, checks):
        validate_identity("apply-url", tenant_id)
        data = _api_request(
            GenerateApplyURLResource(),
            {
                "tenant_id": tenant_id,
                "system_id": settings.BK_IAM_SYSTEM_ID,
                "permissions": self.build_permissions(checks, tenant_id),
            },
        )
        url = data.get("url") if isinstance(data, dict) else None
        if not isinstance(url, str) or not url:
            raise IAMV4ProtocolError("apply URL response missing data.url")
        return url
