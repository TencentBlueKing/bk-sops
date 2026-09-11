from gcloud.iam_auth.conf import RESOURCES_BY_ID
from gcloud.iam_auth.exceptions import IAMResourceNotFound, IAMV4ProtocolError
from gcloud.iam_auth.topology import project_path


def _load_resources(resource_type, resource_id, tenant_id):
    from gcloud.iam_auth.res_factory import resources_for_type

    return resources_for_type(resource_type, resource_id, tenant_id)


def load_resource_for_request(request, resource_type, resource_id):
    """Load a tenant-local resource and validate its route project before trust."""

    tenant_id = getattr(request.user, "tenant_id", "")
    if not tenant_id:
        raise IAMV4ProtocolError("tenant_id is required")
    resources = _load_resources(resource_type, resource_id, tenant_id)
    if len(resources) != 1:
        raise IAMResourceNotFound(resource_type, resource_id)
    resource = resources[0]
    project = getattr(request, "project", None)
    if RESOURCES_BY_ID[resource_type]["parent_id"] == "project" and project is not None:
        actual_path = (resource.attribute or {}).get("_bk_iam_path_", "")
        if actual_path != project_path(project.id):
            raise IAMResourceNotFound(resource_type, resource_id)
    return resource
