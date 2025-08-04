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
from django.views.decorators.http import require_GET

from blueapps.account.decorators import login_exempt
from gcloud import err_code
from gcloud.apigw.decorators import mark_request_whether_is_trust, timezone_inject, return_json_response
from gcloud.apigw.decorators import project_inject, validate_project_access
from gcloud.periodictask.models import PeriodicTask
from gcloud.apigw.views.utils import info_data_from_period_task
from gcloud.iam_auth.intercept import iam_intercept
from gcloud.iam_auth.view_interceptors.apigw import ProjectViewInterceptor
from gcloud.iam_auth.conf import PERIODIC_TASK_ACTIONS
from gcloud.iam_auth.utils import get_periodic_task_allowed_actions_for_user
from apigw_manager.apigw.decorators import apigw_require


@login_exempt
@require_GET
@apigw_require
@return_json_response
@mark_request_whether_is_trust
@project_inject
@validate_project_access
@timezone_inject
@iam_intercept(ProjectViewInterceptor())
def get_periodic_task_list(request, project_id):
    include_edit_info = request.GET.get("include_edit_info", None)
    project = request.project
    task_list = PeriodicTask.objects.filter(project_id=project.id)
    data = []
    task_id_list = []
    for task in task_list:
        task_info = info_data_from_period_task(task, detail=False, tz=request.tz, include_edit_info=include_edit_info)
        task_id_list.append(task_info["id"])
        data.append(task_info)
    # 注入用户有权限的actions
    periodic_task_allowed_actions = get_periodic_task_allowed_actions_for_user(
        request.user.username, PERIODIC_TASK_ACTIONS, task_id_list
    )
    for task_info in data:
        task_id = task_info["id"]
        task_info.setdefault("auth_actions", [])
        for action, allowed in periodic_task_allowed_actions.get(str(task_id), {}).items():
            if allowed:
                task_info["auth_actions"].append(action)
    return {"result": True, "data": data, "code": err_code.SUCCESS.code}
