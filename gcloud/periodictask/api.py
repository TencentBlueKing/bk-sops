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
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST

from gcloud import err_code
from gcloud.common_template.models import CommonTemplate
from gcloud.constants import COMMON, NON_COMMON_TEMPLATE_TYPES
from gcloud.core.models import Project
from gcloud.iam_auth.intercept import iam_intercept
from gcloud.iam_auth.view_interceptors.periodic_task import (
    ModifyConstantsInterceptor,
    ModifyCronInterceptor,
    PeriodicTaskProjectViewInterceptor,
    SetEnabledForPeriodicTaskInterceptor,
)
from gcloud.periodictask.models import PeriodicTask
from gcloud.periodictask.validators import (
    ModifyConstantsValidator,
    ModifyCronValidator,
    SetEnabledForPeriodicTaskValidator,
)
from gcloud.tasktmpl3.models import TaskTemplate
from gcloud.utils.decorators import request_validate


@require_POST
@request_validate(SetEnabledForPeriodicTaskValidator)
@iam_intercept(SetEnabledForPeriodicTaskInterceptor())
def set_enabled_for_periodic_task(request, project_id, task_id):
    data = json.loads(request.body)

    task = PeriodicTask.objects.get(id=task_id)
    task.set_enabled(data["enabled"])
    task.editor = request.user.username
    task.save(update_fields=["editor", "edit_time"])

    return JsonResponse({"result": True, "message": "success"})


@require_POST
@request_validate(ModifyCronValidator)
@iam_intercept(ModifyCronInterceptor())
def modify_cron(request, project_id, task_id):
    data = json.loads(request.body)

    task = PeriodicTask.objects.get(id=task_id)
    project = Project.objects.get(id=project_id)

    try:
        task.modify_cron(data["cron"], data["cron"].get("timezone") or project.time_zone)
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


@require_GET
@iam_intercept(PeriodicTaskProjectViewInterceptor())
def get_period_tasks_with_expired_template(request, project_id):
    """
    获取具有过期模板的周期性任务
    """

    periodic_tasks = list(
        PeriodicTask.objects.filter(project__id=project_id).only(
            "id", "template_id", "template_version", "template_source"
        )
    )

    # 按 template_source 分组，批量查询模板以避免 N+1 查询
    project_tasks = [t for t in periodic_tasks if t.template_source in NON_COMMON_TEMPLATE_TYPES]
    common_tasks = [t for t in periodic_tasks if t.template_source == COMMON]

    # 批量获取模板 id->version 映射
    template_version_map = {}
    if project_tasks:
        template_ids = list({t.template_id for t in project_tasks})
        for tmpl in TaskTemplate.objects.filter(id__in=template_ids).select_related("pipeline_template"):
            template_version_map[tmpl.id] = tmpl.version
    if common_tasks:
        template_ids = list({t.template_id for t in common_tasks})
        for tmpl in CommonTemplate.objects.filter(id__in=template_ids).select_related("pipeline_template"):
            template_version_map[tmpl.id] = tmpl.version

    expired_task_ids = []
    for task in periodic_tasks:
        if task.template_version and template_version_map.get(int(task.template_id)):
            if task.template_version != template_version_map.get(int(task.template_id)):
                expired_task_ids.append(task.id)

    return JsonResponse({"result": True, "data": expired_task_ids, "code": err_code.SUCCESS.code, "message": ""})
