# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from apigw_manager.apigw.decorators import apigw_require
from blueapps.account.decorators import login_exempt
from django.http import JsonResponse
from django.views.decorators.http import require_GET

from gcloud import err_code
from gcloud.apigw.decorators import mark_request_whether_is_trust, mcp_apigw, project_inject, return_json_response
from gcloud.apigw.views.utils import logger
from gcloud.iam_auth.intercept import iam_intercept
from gcloud.iam_auth.view_interceptors.apigw import TaskViewInterceptor
from gcloud.taskflow3.models import TaskFlowInstance
from plugin_service.plugin_client import PluginServiceApiClient


def fetch_task_plugin_log(plugin_code, trace_id, scroll_id=None):
    """获取插件日志的核心逻辑，供内外接口共用"""
    result = PluginServiceApiClient.get_plugin_logs(plugin_code, trace_id, scroll_id)
    if result["result"]:
        logs = [
            f'[{log["ts"]}]{log["detail"]["json.levelname"]}-{log["detail"]["json.funcName"]}: '
            f'{log["detail"]["json.message"]}'
            for log in result["data"]["logs"]
        ]
        result["data"]["logs"] = "\n".join(logs)
    return result


@login_exempt
@require_GET
@apigw_require
@mcp_apigw()
@return_json_response
@mark_request_whether_is_trust
@project_inject
@iam_intercept(TaskViewInterceptor())
def get_task_plugin_log(request, task_id, project_id):
    project = request.project
    try:
        TaskFlowInstance.objects.get(id=task_id, project_id=project.id)
    except TaskFlowInstance.DoesNotExist:
        message = (
            "[API] get_task_plugin_log task[id={task_id}] "
            "of project[project_id={project_id}, biz_id={biz_id}] does not exist".format(
                task_id=task_id, project_id=project.id, biz_id=project.bk_biz_id
            )
        )
        logger.exception(message)
        return {"result": False, "message": message, "code": err_code.CONTENT_NOT_EXIST.code}

    trace_id = request.GET.get("trace_id")
    scroll_id = request.GET.get("scroll_id")
    plugin_code = request.GET.get("plugin_code")

    return JsonResponse(fetch_task_plugin_log(plugin_code, trace_id, scroll_id))
