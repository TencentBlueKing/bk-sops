from django.conf import settings

from gcloud.iam_auth.api_v4.resources import (
    BatchCreateActionResource,
    BatchCreateResourceTypeResource,
    BatchCreateRoleResource,
    CreateSystemResource,
    ListActionResource,
    ListResourceTypeResource,
    ListRoleResource,
    RetrieveSystemResource,
    UpdateActionResource,
    UpdateResourceTypeResource,
    UpdateRoleResource,
    UpdateSystemResource,
)
from gcloud.iam_auth.client import _api_request
from gcloud.iam_auth.exceptions import IAMV4ProtocolError
from gcloud.iam_auth.model_validation import load_models, validate_models


def validate_created_ids(data, expected_ids, object_name):
    if not isinstance(data, list) or any(not isinstance(item, str) for item in data):
        raise IAMV4ProtocolError("{} API data must be a list of ids".format(object_name))
    if len(data) != len(set(data)) or set(data) != set(expected_ids):
        raise IAMV4ProtocolError("{} API response is incomplete".format(object_name))


def validate_list_response(data, object_name):
    if (
        not isinstance(data, dict)
        or not isinstance(data.get("count"), int)
        or not isinstance(data.get("results"), list)
    ):
        raise IAMV4ProtocolError("{} list API returned an invalid response".format(object_name))
    if data["count"] != len(data["results"]):
        raise IAMV4ProtocolError("{} list API response was truncated".format(object_name))
    rows = {}
    for row in data["results"]:
        if not isinstance(row, dict) or not isinstance(row.get("id"), str) or row["id"] in rows:
            raise IAMV4ProtocolError("{} list API returned an invalid row".format(object_name))
        rows[row["id"]] = row
    return rows


def _sync_system(tenant_id, desired):
    current = _api_request(
        RetrieveSystemResource(),
        {"tenant_id": tenant_id, "system_id": desired["id"]},
        allow_not_found=True,
    )
    if current is None:
        payload = dict(desired)
        payload["tenant_id"] = tenant_id
        data = _api_request(CreateSystemResource(), payload)
        if not isinstance(data, dict) or data.get("id") != desired["id"]:
            raise IAMV4ProtocolError("system API response does not match the requested system")
        return "created"
    if not isinstance(current, dict) or current.get("id") != desired["id"]:
        raise IAMV4ProtocolError("system retrieve API returned an invalid response")
    fields = ("name", "description", "managers", "clients", "callback_url")
    changes = {key: desired[key] for key in fields if current.get(key) != desired[key]}
    if changes:
        changes.update({"tenant_id": tenant_id, "system_id": desired["id"]})
        _api_request(UpdateSystemResource(), changes)
        return "updated"
    return "unchanged"


def _sync_resource_types(tenant_id, system_id, desired):
    current = validate_list_response(
        _api_request(
            ListResourceTypeResource(),
            {"tenant_id": tenant_id, "system_id": system_id, "page": 1, "page_size": 100},
        ),
        "resource type",
    )
    missing = [item for item in desired if item["id"] not in current]
    if missing:
        data = _api_request(
            BatchCreateResourceTypeResource(),
            {"tenant_id": tenant_id, "system_id": system_id, "resource_types": missing},
        )
        validate_created_ids(data, [item["id"] for item in missing], "resource type")
    for item in desired:
        existing = current.get(item["id"])
        if existing is None:
            continue
        changes = {key: item[key] for key in ("name", "ancestors") if existing.get(key) != item[key]}
        if changes:
            changes.update({"tenant_id": tenant_id, "system_id": system_id, "resource_type_id": item["id"]})
            _api_request(UpdateResourceTypeResource(), changes)


def _sync_actions(tenant_id, system_id, desired):
    current = validate_list_response(
        _api_request(
            ListActionResource(),
            {"tenant_id": tenant_id, "system_id": system_id, "page": 1, "page_size": 100},
        ),
        "action",
    )
    missing = [item for item in desired if item["id"] not in current]
    if missing:
        data = _api_request(
            BatchCreateActionResource(),
            {"tenant_id": tenant_id, "system_id": system_id, "actions": missing},
        )
        validate_created_ids(data, [item["id"] for item in missing], "action")
    for item in desired:
        existing = current.get(item["id"])
        if existing is None:
            continue
        if (existing.get("resource_type_id") or "") != item["resource_type_id"]:
            raise IAMV4ProtocolError("action resource_type_id cannot be updated: {}".format(item["id"]))
        if existing.get("name") != item["name"]:
            _api_request(
                UpdateActionResource(),
                {
                    "tenant_id": tenant_id,
                    "system_id": system_id,
                    "action_id": item["id"],
                    "name": item["name"],
                },
            )


def _role_action_bindings(role):
    actions = role.get("actions")
    if not isinstance(actions, list):
        raise IAMV4ProtocolError("role actions must be a list: {}".format(role.get("id", "")))
    bindings = []
    for action in actions:
        if not isinstance(action, dict) or not isinstance(action.get("id"), str):
            raise IAMV4ProtocolError("role action is invalid: {}".format(role.get("id", "")))
        bindings.append((action["id"], action.get("resource_type_id") or ""))
    if len(bindings) != len(set(bindings)):
        raise IAMV4ProtocolError("role actions contain duplicates: {}".format(role.get("id", "")))
    return set(bindings)


def _sync_roles(tenant_id, system_id, desired):
    current = validate_list_response(
        _api_request(
            ListRoleResource(),
            {"tenant_id": tenant_id, "system_id": system_id, "page": 1, "page_size": 100},
        ),
        "role",
    )
    missing = [item for item in desired if item["id"] not in current]
    if missing:
        data = _api_request(
            BatchCreateRoleResource(),
            {"tenant_id": tenant_id, "system_id": system_id, "roles": missing},
        )
        validate_created_ids(data, [item["id"] for item in missing], "role")
    for item in desired:
        existing = current.get(item["id"])
        if existing is None:
            continue
        if _role_action_bindings(existing) != _role_action_bindings(item):
            raise IAMV4ProtocolError("role actions cannot be updated: {}".format(item["id"]))
        changes = {
            key: item.get(key, "") for key in ("name", "description") if existing.get(key, "") != item.get(key, "")
        }
        if changes:
            changes.update({"tenant_id": tenant_id, "system_id": system_id, "role_id": item["id"]})
            _api_request(UpdateRoleResource(), changes)


def register_roles(tenant_id):
    """Validate and idempotently synchronize IAM V4 roles through the gateway."""

    model, roles = load_models()
    validate_models(model, roles)
    _sync_roles(tenant_id, settings.BK_IAM_SYSTEM_ID, roles)
    return {"roles": len(roles)}


def register_base_model(tenant_id):
    """Register the complete V4 model exclusively through the IAM API gateway."""

    model, roles = load_models()
    validate_models(model, roles)
    system = model["system"]
    system_status = _sync_system(tenant_id, system)
    resource_types = model["resource_types"]
    _sync_resource_types(tenant_id, settings.BK_IAM_SYSTEM_ID, resource_types)
    actions = model["actions"]
    _sync_actions(tenant_id, settings.BK_IAM_SYSTEM_ID, actions)
    _sync_roles(tenant_id, settings.BK_IAM_SYSTEM_ID, roles)
    return {
        "systems": 1,
        "system_status": system_status,
        "resources": len(resource_types),
        "actions": len(actions),
        "roles": len(roles),
    }
