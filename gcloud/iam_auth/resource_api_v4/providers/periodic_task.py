from gcloud.iam_auth.resource_api_v4.providers.base import ProviderSpec, ResourceProvider


class PeriodicTaskResourceProvider(ResourceProvider):
    def __init__(self):
        super().__init__(ProviderSpec("periodic_task", "task__name", "project_id", ("creator", "editor")))
