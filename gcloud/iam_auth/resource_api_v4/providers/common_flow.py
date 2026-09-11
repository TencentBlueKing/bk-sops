from gcloud.iam_auth.resource_api_v4.providers.base import ProviderSpec, ResourceProvider


class CommonFlowResourceProvider(ResourceProvider):
    def __init__(self):
        super().__init__(
            ProviderSpec(
                "common_flow",
                "pipeline_template__name",
                approver_lookups=("pipeline_template__creator", "pipeline_template__editor"),
            )
        )
