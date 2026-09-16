import json
from pathlib import Path
from urllib.parse import urlparse

from django.conf import settings

from gcloud.iam_auth.conf import ACTION_RESOURCE_TYPES, ACTIONS, RESOURCE_TYPE_IDS, RESOURCES, RESOURCES_BY_ID
from gcloud.iam_auth.exceptions import IAMV4ProtocolError

ALLOWED_ROLE_BINDINGS = {
    None: {""},
    "project": {"project"},
    "flow": {"flow", "project"},
    "task": {"task", "project"},
    "common_flow": {"common_flow"},
    "mini_app": {"mini_app", "project"},
    "periodic_task": {"periodic_task", "project"},
    "clocked_task": {"clocked_task", "project"},
}


def _bindings(spec):
    return frozenset(tuple(item.split("@", 1)) for item in spec.split())


# Keep the v1.1 role semantics independent from roles.json so accidental edits to
# the deployment artifact cannot silently pass validation.
EXPECTED_ROLE_BINDINGS = {
    "biz_operator": _bindings(
        """
        project_view@project project_edit@project flow_create@project
        project_fast_create_task@project project_common_create_task@project
        project_common_create_periodic@project flow_view@project flow_edit@project
        flow_delete@project flow_create_task@project flow_create_mini_app@project
        flow_create_periodic_task@project flow_create_clocked_task@project
        task_view@project task_edit@project task_operate@project task_delete@project
        task_clone@project mini_app_view@project mini_app_edit@project
        mini_app_delete@project mini_app_create_task@project periodic_task_view@project
        periodic_task_edit@project periodic_task_delete@project clocked_task_view@project
        clocked_task_edit@project clocked_task_delete@project common_flow_view@common_flow
        common_flow_create_task@common_flow common_flow_create_periodic_task@common_flow
        """
    ),
    "biz_flow_executor": _bindings("project_view@project flow_view@flow flow_create_task@flow"),
    "mini_app_user": _bindings(
        "project_view@project flow_view@flow mini_app_view@mini_app mini_app_create_task@mini_app"
    ),
    "biz_viewer": _bindings(
        """
        project_view@project flow_view@project task_view@project mini_app_view@project
        periodic_task_view@project clocked_task_view@project
        """
    ),
    "common_flow_developer": _bindings("common_flow_create@ common_flow_view@common_flow common_flow_edit@common_flow"),
    "biz_function_executor": _bindings(
        """
        project_view@project function_task_view@project task_view@task
        task_claim@task task_operate@task
        """
    ),
    "vendor_flow_executor": _bindings("project_view@project flow_view@flow flow_create_task@flow"),
    "platform_auditor": _bindings(
        """
        audit_view@ function_view@ statistics_view@ project_view@project
        function_task_view@project flow_view@project task_view@project
        mini_app_view@project periodic_task_view@project clocked_task_view@project
        common_flow_view@common_flow
        """
    ),
}
EXPECTED_ROLE_BINDINGS["platform_admin"] = frozenset(
    (
        action_id,
        "" if resource_type is None else "common_flow" if resource_type == "common_flow" else "project",
    )
    for action_id, resource_type in ACTION_RESOURCE_TYPES.items()
)


def load_models():
    base_dir = Path(settings.BASE_DIR)
    with (base_dir / "support-files/iam-v4/roles.json").open(encoding="utf-8") as file:
        roles = json.load(file)
    callback_host = getattr(settings, "BK_IAM_RESOURCE_API_HOST", "").rstrip("/")
    managers = list(getattr(settings, "IAM_V4_SYSTEM_MANAGERS", ()))
    system = {
        "id": settings.BK_IAM_SYSTEM_ID,
        "name": settings.BK_IAM_SYSTEM_NAME,
        "description": "",
        "clients": [settings.APP_CODE],
        "callback_url": "{}/iam/resource/api/v4/".format(callback_host) if callback_host else "",
    }
    if managers:
        system["managers"] = managers
    model = {
        "system": system,
        "resource_types": [
            {
                "id": item["id"],
                "name": str(item["name"]),
                "ancestors": [item["parent_id"]] if item["parent_id"] else [],
            }
            for item in RESOURCES
        ],
        "actions": [
            {
                "id": item["id"],
                "name": str(item["name"]),
                "resource_type_id": ACTION_RESOURCE_TYPES[item["id"]] or "",
            }
            for item in ACTIONS
        ],
    }
    return model, roles


def validate_models(model, roles):
    if not isinstance(model, dict) or not isinstance(roles, list):
        raise IAMV4ProtocolError("IAM V4 model files have invalid roots")
    system = model.get("system")
    resources = model.get("resource_types")
    actions = model.get("actions")
    if not isinstance(system, dict) or system.get("id") != settings.BK_IAM_SYSTEM_ID:
        raise IAMV4ProtocolError("model must contain one matching system")
    clients = set(system.get("clients", []))
    if settings.APP_CODE not in clients:
        raise IAMV4ProtocolError("model system clients must include current application")
    callback_url = system.get("callback_url", "")
    parsed_callback_url = urlparse(callback_url)
    if parsed_callback_url.scheme not in {"http", "https"} or not parsed_callback_url.netloc:
        raise IAMV4ProtocolError("model system callback_url must be an absolute HTTP URL")
    allowed_system_fields = {"id", "name", "description", "managers", "clients", "callback_url"}
    if set(system) - allowed_system_fields:
        raise IAMV4ProtocolError("model system contains fields outside the IAM V4 gateway contract")
    if not isinstance(resources, list) or not isinstance(actions, list):
        raise IAMV4ProtocolError("model resource_types and actions must be lists")
    resource_ids = [item.get("id") for item in resources]
    if len(resources) != 7 or set(resource_ids) != set(RESOURCE_TYPE_IDS):
        raise IAMV4ProtocolError("model resource types do not match code")
    if any(set(item) - {"id", "name", "ancestors"} for item in resources):
        raise IAMV4ProtocolError("resource type contains fields outside the IAM V4 gateway contract")
    action_ids = [item.get("id") for item in actions]
    if len(actions) != 42 or len(set(action_ids)) != 42 or set(action_ids) != set(ACTION_RESOURCE_TYPES):
        raise IAMV4ProtocolError("model actions do not match code")
    for item in actions:
        if set(item) - {"id", "name", "resource_type_id"}:
            raise IAMV4ProtocolError("action contains fields outside the IAM V4 gateway contract")
        actual = item.get("resource_type_id") or None
        if actual != ACTION_RESOURCE_TYPES[item["id"]]:
            raise IAMV4ProtocolError("action resource type does not match code: {}".format(item["id"]))

    parents = {item["id"]: item.get("ancestors", []) for item in resources}
    expected_parents = {
        resource_id: [meta["parent_id"]] if meta["parent_id"] else [] for resource_id, meta in RESOURCES_BY_ID.items()
    }
    if parents != expected_parents:
        raise IAMV4ProtocolError("resource parents do not match code topology")
    for resource_id in parents:
        seen = set()
        current = resource_id
        while parents[current]:
            current = parents[current][0]
            if current in seen or current not in parents:
                raise IAMV4ProtocolError("resource parent topology is invalid")
            seen.add(current)

    role_ids = [role.get("id") for role in roles]
    if len(roles) != 9 or set(role_ids) != set(EXPECTED_ROLE_BINDINGS):
        raise IAMV4ProtocolError("roles.json must contain exactly 9 unique roles")
    for role in roles:
        role_action_ids = [item.get("id") for item in role.get("actions", [])]
        if not role_action_ids or len(role_action_ids) != len(set(role_action_ids)):
            raise IAMV4ProtocolError("role contains no actions or duplicate actions: {}".format(role["id"]))
        for item in role["actions"]:
            action_id = item.get("id")
            if action_id not in ACTION_RESOURCE_TYPES:
                raise IAMV4ProtocolError("role references unknown action: {}".format(action_id))
            if item.get("resource_type_id") not in ALLOWED_ROLE_BINDINGS[ACTION_RESOURCE_TYPES[action_id]]:
                raise IAMV4ProtocolError("role action binding is invalid: {}".format(action_id))
        actual_bindings = frozenset((item["id"], item.get("resource_type_id", "")) for item in role["actions"])
        if actual_bindings != EXPECTED_ROLE_BINDINGS[role["id"]]:
            raise IAMV4ProtocolError("role does not match the v1.1 model: {}".format(role["id"]))
    auditor = next(role for role in roles if role["id"] == "platform_auditor")
    auditor_actions = {item["id"] for item in auditor["actions"]}
    if "admin_view" in auditor_actions or any(
        action_id.endswith(("_edit", "_delete", "_create")) for action_id in auditor_actions
    ):
        raise IAMV4ProtocolError("platform_auditor contains a sensitive action")
    return {"systems": 1, "resources": 7, "actions": 42, "roles": 9}


def validate_local_models():
    return validate_models(*load_models())
