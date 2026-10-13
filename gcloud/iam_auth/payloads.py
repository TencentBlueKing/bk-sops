from gcloud.iam_auth.conf import RESOURCES_BY_ID
from gcloud.iam_auth.exceptions import IAMV4ProtocolError
from gcloud.iam_auth.topology import parse_iam_path


def resource_to_v4_auth(resource):
    if resource is None:
        return None
    # IAM determines the resource type from the action.  For a child resource,
    # its registered ancestors must be supplied so project-scoped grants match.
    resource_info = RESOURCES_BY_ID.get(resource.type)
    if resource_info is None:
        raise IAMV4ProtocolError("unknown auth resource type")
    payload = {"id": str(resource.id)}
    ancestor_types = []
    parent_id = resource_info["parent_id"]
    while parent_id:
        ancestor_types.insert(0, parent_id)
        parent_id = RESOURCES_BY_ID[parent_id]["parent_id"]
    if ancestor_types:
        path = (resource.attribute or {}).get("_bk_iam_path_", "")
        if [ancestor["type"] for ancestor in parse_iam_path(path)] != ancestor_types:
            raise IAMV4ProtocolError("auth resource is missing a valid _bk_iam_path_")
        payload["attributes"] = {"_bk_iam_path_": path}
    return payload


def resource_to_v4_apply(resource):
    if resource is None:
        return None
    payload = {"type": resource.type, "id": str(resource.id)}
    ancestors = parse_iam_path((resource.attribute or {}).get("_bk_iam_path_", ""))
    if ancestors:
        payload["ancestors"] = ancestors
    return payload
