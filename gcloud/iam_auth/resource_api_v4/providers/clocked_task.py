from gcloud.iam_auth.resource_api_v4.providers.base import ProviderSpec, ResourceProvider


class ClockedTaskResourceProvider(ResourceProvider):
    def __init__(self):
        super().__init__(ProviderSpec("clocked_task", "task_name", "project_id", ("creator", "editor")))
