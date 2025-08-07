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


import ujson as json
from apigw_manager.apigw.decorators import apigw_require
from blueapps.account.decorators import login_exempt
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from gcloud import err_code
from gcloud.apigw.decorators import mark_request_whether_is_trust, project_inject, return_json_response
from gcloud.contrib.operate_record.constants import OperateSource, OperateType, RecordType
from gcloud.contrib.operate_record.decorators import record_operation
from gcloud.core.trace import CallFrom, trace_view
from gcloud.iam_auth.intercept import iam_intercept
from gcloud.iam_auth.view_interceptors.apigw import TaskOperateInterceptor
from gcloud.taskflow3.models import TaskFlowInstance


@login_exempt
@csrf_exempt
@require_POST
@apigw_require
@return_json_response
@mark_request_whether_is_trust
@project_inject
@trace_view(attr_keys=["project_id", "task_id"], call_from=CallFrom.APIGW.value)
@iam_intercept(TaskOperateInterceptor())
@record_operation(RecordType.task.name, OperateType.nodes_action.name, OperateSource.api.name)
def operate_node(request, project_id, task_id):
    try:
        req_data = json.loads(request.body)
    except Exception:
        return {
            "result": False,
            "message": "request body is not a valid json",
            "code": err_code.REQUEST_PARAM_INVALID.code,
        }

    username = request.user.username
    node_id = req_data.get("node_id")
    action = req_data.get("action")

    data = req_data.get("data", {})
    if not isinstance(data, dict):
        return {
            "result": False,
            "message": "data field is not a valid object",
            "code": err_code.REQUEST_PARAM_INVALID.code,
        }

    inputs = req_data.get("inputs", {})
    if not isinstance(inputs, dict):
        return {
            "result": False,
            "message": "inputs field is not a valid object",
            "code": err_code.REQUEST_PARAM_INVALID.code,
        }

    kwargs = {
        "data": data,
        "inputs": inputs,
        "flow_id": req_data.get("flow_id", ""),
    }
    task = TaskFlowInstance.objects.get(pk=task_id)
    result = task.nodes_action(action, node_id, username, **kwargs)
    result["code"] = err_code.SUCCESS.code if result["result"] else err_code.UNKNOWN_ERROR.code
    return result
