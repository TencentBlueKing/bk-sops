from gcloud.iam_auth.topology import parse_iam_path


def resource_to_v4_auth(resource):
    if resource is None:
        return None
    # IAM V4 determines the resource type from the action model.  The gateway
    # contract accepts only the instance id here; type/attributes are V3 fields.
    return {"id": str(resource.id)}


def resource_to_v4_apply(resource):
    if resource is None:
        return None
    payload = {"type": resource.type, "id": str(resource.id)}
    ancestors = parse_iam_path((resource.attribute or {}).get("_bk_iam_path_", ""))
    if ancestors:
        payload["ancestors"] = ancestors
    return payload
