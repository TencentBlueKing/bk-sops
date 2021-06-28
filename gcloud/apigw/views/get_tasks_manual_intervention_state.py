# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import logging
import ujson as json

from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from blueapps.account.decorators import login_exempt
from gcloud import err_code
from gcloud.apigw.decorators import mark_request_whether_is_trust
from gcloud.apigw.decorators import project_inject
from gcloud.taskflow3.models import TaskFlowInstance
from gcloud.iam_auth.intercept import iam_intercept
from gcloud.iam_auth.view_interceptors.apigw import ProjectViewInterceptor
from packages.bkoauth.decorators import apigw_required

logger = logging.getLogger("root")


@csrf_exempt
@login_exempt
@require_POST
@apigw_required
@mark_request_whether_is_trust
@project_inject
@iam_intercept(ProjectViewInterceptor())
def get_tasks_manual_intervention_state(request, project_id):
    try:
        params = json.loads(request.body)
    except Exception:
        return {
            "result": False,
            "message": "request body is not a valid json",
            "code": err_code.REQUEST_PARAM_INVALID.code,
        }

    task_ids = params.get("task_id_list", [])
    if not isinstance(task_ids, list):
        return {"result": False, "message": "task_id_list must be a list", "code": err_code.REQUEST_PARAM_INVALID.code}

    if len(task_ids) >= 10:
        return {
            "result": False,
            "message": "task_ids_list length can not exceeds 10",
            "code": err_code.REQUEST_PARAM_INVALID.code,
        }

    tasks = TaskFlowInstance.objects.filter(id__in=task_ids, project__id=request.project.id)

    data = []
    for task in tasks:
        try:
            data.append({"id": task.id, "manual_intervention_required": task.is_manual_intervention_required})
        except Exception:
            logger.exception("task.is_manual_intervention_required get fail")
            return {
                "result": False,
                "data": None,
                "message": "task.is_manual_intervention_required get fail",
                "code": err_code.UNKNOWN_ERROR.code,
            }

    return {"result": True, "data": data, "code": err_code.SUCCESS.code}
