from gcloud.iam_auth.resource_api_v4.providers.base import ProviderSpec, ResourceProvider


class MiniAppResourceProvider(ResourceProvider):
    def __init__(self):
        super().__init__(ProviderSpec("mini_app", "name", "project_id", ("creator", "editor")))
