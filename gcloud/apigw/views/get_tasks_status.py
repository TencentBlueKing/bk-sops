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
from gcloud.core.utils import format_datetime
from gcloud.core.permissions import project_resource
from gcloud.apigw.decorators import api_verify_proj_perms
from gcloud.apigw.decorators import mark_request_whether_is_trust
from gcloud.apigw.decorators import project_inject
from gcloud.taskflow3.models import TaskFlowInstance

try:
    from bkoauth.decorators import apigw_required
except ImportError:
    from packages.bkoauth.decorators import apigw_required


@csrf_exempt
@login_exempt
@require_POST
@apigw_required
@mark_request_whether_is_trust
@project_inject
@api_verify_proj_perms([project_resource.actions.view])
def get_tasks_status(request, project_id):

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

    task_ids = params.get("task_id_list", [])
    if not isinstance(task_ids, list):
        return JsonResponse(
            {"result": False, "message": "task_id_list must be a list", "code": err_code.REQUEST_PARAM_INVALID.code}
        )
    include_children_status = params.get("include_children_status", False)

    tasks = TaskFlowInstance.objects.filter(id__in=task_ids, project__id=request.project.id)

    data = []
    for task in tasks:
        status = task.get_status()

        if not include_children_status:
            status.pop("children")

        data.append(
            {
                "id": task.id,
                "name": task.name,
                "status": status,
                "create_time": format_datetime(task.create_time),
                "start_time": format_datetime(task.start_time),
                "finish_time": format_datetime(task.finish_time),
                "url": task.url,
            }
        )

    return JsonResponse({"result": True, "data": data, "code": err_code.SUCCESS.code})
