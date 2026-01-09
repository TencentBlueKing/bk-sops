from apigw_manager.apigw.decorators import apigw_require
from blueapps.account.decorators import login_exempt
from django.http import JsonResponse
from rest_framework.decorators import api_view

from gcloud.apigw.decorators import mark_request_whether_is_trust, project_inject, return_json_response
from gcloud.iam_auth.intercept import iam_intercept
from gcloud.iam_auth.view_interceptors.apigw import TaskViewInterceptor
from plugin_service.api_decorators import validate_params
from plugin_service.plugin_client import PluginServiceApiClient
from plugin_service.serializers import LogQuerySerializer


@login_exempt
@api_view(["GET"])
@apigw_require
@return_json_response
@mark_request_whether_is_trust
@project_inject
@iam_intercept(TaskViewInterceptor())
@validate_params(LogQuerySerializer)
def get_task_plugin_log(request):
    trace_id = request.validated_data.get("trace_id")
    scroll_id = request.validated_data.get("scroll_id")
    plugin_code = request.validated_data.get("plugin_code")
    result = PluginServiceApiClient.get_plugin_logs(plugin_code, trace_id, scroll_id)
    if result["result"]:
        logs = [
            f'[{log["ts"]}]{log["detail"]["json.levelname"]}-{log["detail"]["json.funcName"]}: '
            f'{log["detail"]["json.message"]}'
            for log in result["data"]["logs"]
        ]
        result["data"]["logs"] = "\n".join(logs)
    return JsonResponse(result)
