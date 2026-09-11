from gcloud.iam_auth.resource_api_v4.providers.base import ProviderSpec, ResourceProvider


class ProjectResourceProvider(ResourceProvider):
    def __init__(self):
        super().__init__(ProviderSpec("project", "name", approver_lookups=("creator",)))
