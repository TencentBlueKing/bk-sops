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
from rest_framework.decorators import api_view
from rest_framework.response import Response

from gcloud.apigw.decorators import mark_request_whether_is_trust, mcp_apigw, project_inject
from gcloud.apigw.log_auth import get_taskflow_for_log, validate_node_plugin_trace, validate_task_node
from gcloud.iam_auth.intercept import iam_intercept
from gcloud.iam_auth.view_interceptors.apigw import TaskViewInterceptor
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
@api_view(["GET"])
@apigw_require
@mcp_apigw()
@mark_request_whether_is_trust
@project_inject
@iam_intercept(TaskViewInterceptor())
def get_task_plugin_log(request, task_id, project_id):
    project = request.project
    taskflow, error_response = get_taskflow_for_log("get_task_plugin_log", task_id, project)
    if error_response is not None:
        return error_response

    node_id = request.GET.get("node_id")
    trace_id = request.GET.get("trace_id")
    scroll_id = request.GET.get("scroll_id")
    plugin_code = request.GET.get("plugin_code")
    error_response = validate_task_node("get_task_plugin_log", taskflow, node_id)
    if error_response is not None:
        return error_response

    error_response = validate_node_plugin_trace("get_task_plugin_log", node_id, trace_id, plugin_code)
    if error_response is not None:
        return error_response

    return Response(fetch_task_plugin_log(plugin_code, trace_id, scroll_id))
