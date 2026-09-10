from gcloud.iam_auth.resource_api_v4.providers.base import ProviderSpec, ResourceProvider


class TaskResourceProvider(ResourceProvider):
    def __init__(self):
        super().__init__(
            ProviderSpec(
                "task",
                "pipeline_instance__name",
                "project_id",
                ("pipeline_instance__creator", "pipeline_instance__executor"),
            )
        )
