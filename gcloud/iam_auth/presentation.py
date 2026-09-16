from collections import OrderedDict

from django.conf import settings

from gcloud.iam_auth.conf import ACTIONS_BY_ID, RESOURCE_NAMES
from gcloud.iam_auth.topology import parse_iam_path


def _instance_chain(resource):
    chain = []
    for ancestor in parse_iam_path((resource.attribute or {}).get("_bk_iam_path_", "")):
        chain.append(
            {
                "type": ancestor["type"],
                "type_name": RESOURCE_NAMES[ancestor["type"]],
                "id": ancestor["id"],
                "name": ancestor["id"],
            }
        )
    chain.append(
        {
            "type": resource.type,
            "type_name": RESOURCE_NAMES[resource.type],
            "id": str(resource.id),
            "name": (resource.attribute or {}).get("name", str(resource.id)),
        }
    )
    return chain


def serialize_missing_permissions(checks):
    actions = OrderedDict()
    for check in checks:
        action_meta = ACTIONS_BY_ID[check.action_id]
        action = actions.setdefault(
            check.action_id,
            {"id": check.action_id, "name": action_meta["name"], "related_resource_types": []},
        )
        if check.resource is None:
            continue
        related = next(
            (item for item in action["related_resource_types"] if item["type"] == check.resource.type),
            None,
        )
        if related is None:
            related = {
                "system_id": settings.BK_IAM_SYSTEM_ID,
                "system_name": settings.BK_IAM_SYSTEM_NAME,
                "type": check.resource.type,
                "type_name": RESOURCE_NAMES[check.resource.type],
                "instances": [],
            }
            action["related_resource_types"].append(related)
        related["instances"].append(_instance_chain(check.resource))
    return {
        "system_id": settings.BK_IAM_SYSTEM_ID,
        "system_name": settings.BK_IAM_SYSTEM_NAME,
        "actions": list(actions.values()),
    }
