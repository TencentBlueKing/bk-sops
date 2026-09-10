from gcloud.iam_auth.resource_api_v4.providers.clocked_task import ClockedTaskResourceProvider
from gcloud.iam_auth.resource_api_v4.providers.common_flow import CommonFlowResourceProvider
from gcloud.iam_auth.resource_api_v4.providers.flow import FlowResourceProvider
from gcloud.iam_auth.resource_api_v4.providers.mini_app import MiniAppResourceProvider
from gcloud.iam_auth.resource_api_v4.providers.periodic_task import PeriodicTaskResourceProvider
from gcloud.iam_auth.resource_api_v4.providers.project import ProjectResourceProvider
from gcloud.iam_auth.resource_api_v4.providers.task import TaskResourceProvider

PROVIDERS = {
    "project": ProjectResourceProvider(),
    "flow": FlowResourceProvider(),
    "task": TaskResourceProvider(),
    "common_flow": CommonFlowResourceProvider(),
    "mini_app": MiniAppResourceProvider(),
    "periodic_task": PeriodicTaskResourceProvider(),
    "clocked_task": ClockedTaskResourceProvider(),
}

__all__ = ["PROVIDERS"]
