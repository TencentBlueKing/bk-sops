from gcloud.iam_auth.resource_api_v4.providers.base import ProviderSpec, ResourceProvider


class FlowResourceProvider(ResourceProvider):
    def __init__(self):
        super().__init__(
            ProviderSpec(
                "flow",
                "pipeline_template__name",
                "project_id",
                ("pipeline_template__creator", "pipeline_template__editor"),
            )
        )
