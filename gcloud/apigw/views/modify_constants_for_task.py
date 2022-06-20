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
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from blueapps.account.decorators import login_exempt
from gcloud import err_code
from gcloud.apigw.decorators import mark_request_whether_is_trust, return_json_response
from gcloud.apigw.decorators import project_inject
from gcloud.iam_auth.intercept import iam_intercept
from gcloud.iam_auth.view_interceptors.apigw import TaskEditInterceptor
from gcloud.taskflow3.models import TaskFlowInstance
from apigw_manager.apigw.decorators import apigw_require


@login_exempt
@csrf_exempt
@require_POST
@apigw_require
@return_json_response
@mark_request_whether_is_trust
@project_inject
@iam_intercept(TaskEditInterceptor())
def modify_constants_for_task(request, task_id, project_id):
    project = request.project
    try:
        params = json.loads(request.body)
    except Exception:
        return {"result": False, "message": "invalid json format", "code": err_code.REQUEST_PARAM_INVALID.code}

    task = TaskFlowInstance.objects.get(pk=task_id, project_id=project.id)

    if task.is_started:
        return {"result": False, "message": "task is started", "code": err_code.REQUEST_PARAM_INVALID.code}

    if task.is_finished:
        return {"result": False, "message": "task is finished", "code": err_code.REQUEST_PARAM_INVALID.code}

    constants = params.get("constants", {})
    reset_result = task.set_task_constants(constants)

    if reset_result["result"] is False:
        return {"result": False, "message": reset_result["message"], "code": err_code.REQUEST_PARAM_INVALID.code}

    return {"result": True, "data": reset_result["data"], "code": err_code.SUCCESS.code}
