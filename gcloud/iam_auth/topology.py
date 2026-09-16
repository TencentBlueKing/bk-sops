from gcloud.iam_auth.exceptions import IAMV4ProtocolError


def project_path(project_id):
    if project_id in (None, ""):
        raise IAMV4ProtocolError("project id is required for IAM topology")
    return "/project,{}/".format(project_id)


def project_ancestors(project_id):
    return [{"type": "project", "id": str(project_id)}]


def parse_iam_path(path):
    if not path:
        return []
    if not isinstance(path, str) or not path.startswith("/") or not path.endswith("/"):
        raise IAMV4ProtocolError("invalid _bk_iam_path_ format")

    ancestors = []
    for part in path.strip("/").split("/"):
        resource_type, separator, resource_id = part.partition(",")
        if not separator or not resource_type or not resource_id:
            raise IAMV4ProtocolError("invalid _bk_iam_path_ segment")
        ancestors.append({"type": resource_type, "id": resource_id})
    return ancestors
