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

from gcloud import err_code
from gcloud.core.models import Project

from gcloud.utils.decorators import request_validate
from gcloud.periodictask.models import PeriodicTask
from gcloud.periodictask.validators import (
    SetEnabledForPeriodicTaskValidator,
    ModifyCronValidator,
    ModifyConstantsValidator,
)
from gcloud.iam_auth.intercept import iam_intercept
from gcloud.iam_auth.view_interceptors.periodic_task import (
    SetEnabledForPeriodicTaskInterceptor,
    ModifyCronInterceptor,
    ModifyConstantsInterceptor,
)


@require_POST
@request_validate(SetEnabledForPeriodicTaskValidator)
@iam_intercept(SetEnabledForPeriodicTaskInterceptor())
def set_enabled_for_periodic_task(request, project_id, task_id):
    data = json.loads(request.body)

    task = PeriodicTask.objects.get(id=task_id)
    task.set_enabled(data["enabled"])

    return JsonResponse({"result": True, "message": "success"})


@require_POST
@request_validate(ModifyCronValidator)
@iam_intercept(ModifyCronInterceptor())
def modify_cron(request, project_id, task_id):

    data = json.loads(request.body)

    task = PeriodicTask.objects.get(id=task_id)
    project = Project.objects.get(id=project_id)

    try:
        task.modify_cron(data["cron"], project.time_zone)
    except Exception as e:
        return JsonResponse(
            {"result": False, "message": str(e), "data": None, "code": err_code.REQUEST_PARAM_INVALID.code}
        )

    return JsonResponse({"result": True, "message": "success", "data": None, "code": err_code.SUCCESS.code})


@require_POST
@request_validate(ModifyConstantsValidator)
@iam_intercept(ModifyConstantsInterceptor())
def modify_constants(request, project_id, task_id):
    data = json.loads(request.body)

    task = PeriodicTask.objects.get(id=task_id)

    try:
        new_constants = task.modify_constants(data["constants"])
    except Exception as e:
        return JsonResponse(
            {"result": False, "message": str(e), "data": None, "code": err_code.REQUEST_PARAM_INVALID.code}
        )

    return JsonResponse({"result": True, "message": "success", "data": new_constants, "code": err_code.SUCCESS.code})
