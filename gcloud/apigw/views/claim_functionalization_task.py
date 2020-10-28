# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""


import ujson as json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from blueapps.account.decorators import login_exempt
from gcloud import err_code
from gcloud.apigw.decorators import mark_request_whether_is_trust
from gcloud.apigw.decorators import project_inject
from gcloud.iam_auth.view_interceptors.taskflow import TaskFuncClaimInterceptor
from gcloud.taskflow3.models import TaskFlowInstance
from gcloud.apigw.views.utils import logger
from gcloud.iam_auth.intercept import iam_intercept

try:
    from bkoauth.decorators import apigw_required
except ImportError:
    from packages.bkoauth.decorators import apigw_required


@login_exempt
@csrf_exempt
@require_POST
@apigw_required
@mark_request_whether_is_trust
@project_inject
@iam_intercept(TaskFuncClaimInterceptor())
def claim_functionalization_task(request, task_id, project_id):
    try:
        params = json.loads(request.body)
    except Exception:
        return JsonResponse(
            {
                "result": False,
                "message": "request body is not a valid json",
                "code": err_code.REQUEST_PARAM_INVALID.code,
            }
        )

    constants = params.get("constants", {})
    name = params.get("name", "")

    try:
        task = TaskFlowInstance.objects.get(pk=task_id, project_id=request.project.id)
        result = task.task_claim(request.user.username, constants, name)
    except Exception as e:
        logger.exception("[API] claim_functionalization_task fail: {}".format(e))
        return JsonResponse(
            {
                "result": False,
                "message": "claim_functionalization_task fail: {}".format(e),
                "code": err_code.UNKNOWN_ERROR.code,
            }
        )

    if result["result"] is False:
        return JsonResponse({"result": False, "message": result["message"], "code": err_code.UNKNOWN_ERROR.code})
    return JsonResponse({"result": True, "data": result["message"], "code": err_code.SUCCESS.code})
