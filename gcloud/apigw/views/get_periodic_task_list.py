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
from django.views.decorators.http import require_GET

from gcloud import err_code
from gcloud.apigw.decorators import mark_request_whether_is_trust, project_inject, return_json_response, timezone_inject
from gcloud.apigw.views.utils import info_data_from_period_task
from gcloud.iam_auth.conf import PERIODIC_TASK_ACTIONS
from gcloud.iam_auth.intercept import iam_intercept
from gcloud.iam_auth.utils import get_periodic_task_allowed_actions_for_user
from gcloud.iam_auth.view_interceptors.apigw import ProjectViewInterceptor
from gcloud.periodictask.models import PeriodicTask


@login_exempt
@require_GET
@apigw_require
@return_json_response
@mark_request_whether_is_trust
@project_inject
@timezone_inject
@iam_intercept(ProjectViewInterceptor())
def get_periodic_task_list(request, project_id):
    project = request.project
    tenant_id = request.user.tenant_id
    task_list = PeriodicTask.objects.filter(project_id=project.id, project__tenant_id=tenant_id)
    data = []
    task_id_list = []
    for task in task_list:
        task_info = info_data_from_period_task(task, detail=False, tz=request.tz)
        task_id_list.append(task_info["id"])
        data.append(task_info)
    # 注入用户有权限的actions
    periodic_task_allowed_actions = get_periodic_task_allowed_actions_for_user(
        request.user.username, PERIODIC_TASK_ACTIONS, task_id_list, tenant_id
    )
    for task_info in data:
        task_id = task_info["id"]
        task_info.setdefault("auth_actions", [])
        for action, allowed in periodic_task_allowed_actions.get(str(task_id), {}).items():
            if allowed:
                task_info["auth_actions"].append(action)
    return {"result": True, "data": data, "code": err_code.SUCCESS.code}
