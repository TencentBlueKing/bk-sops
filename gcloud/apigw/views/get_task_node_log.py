from apigw_manager.apigw.decorators import apigw_require
from blueapps.account.decorators import login_exempt
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response

from gcloud.apigw.decorators import mark_request_whether_is_trust, project_inject, return_json_response
from gcloud.iam_auth.intercept import iam_intercept
from gcloud.iam_auth.view_interceptors.apigw import TaskViewInterceptor
from gcloud.taskflow3.domains.node_log import NodeLogDataSourceFactory
from gcloud.utils.handlers import handle_plain_log

DEFAULT_PAGE = 1
DEFAULT_PAGE_SIZE = 30


@login_exempt
@api_view(["GET"])
@apigw_require
@return_json_response
@mark_request_whether_is_trust
@project_inject
@iam_intercept(TaskViewInterceptor())
def get_task_node_log(request, project_id, task_id, node_id, version):
    page = request.query_params.get("page", DEFAULT_PAGE)
    page_size = request.query_params.get("page_size", DEFAULT_PAGE_SIZE)
    data_source = NodeLogDataSourceFactory(settings.NODE_LOG_DATA_SOURCE).data_source
    result = data_source.fetch_node_logs(node_id, version, page=page, page_size=page_size)
    if not result["result"]:
        return Response({"result": False, "message": result["message"], "data": None})
    logs, page_info = result["data"]["logs"], result["data"]["page_info"]

    return Response(
        {
            "result": True,
            "message": "success",
            "data": handle_plain_log(logs),
            "page": page_info if page_info else {},
        }
    )
