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

superuser command
"""
import logging
from itertools import product

from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse
from drf_yasg.utils import swagger_auto_schema
from iam.api.client import Client
from rest_framework.decorators import api_view

import env
from gcloud import err_code
from gcloud.contrib.admin.utils import force_tasks
from gcloud.core.decorators import check_is_superuser
from gcloud.core.models import ProjectBasedComponent
from gcloud.core.tasks import migrate_pipeline_parent_data_task, scan_periodic_task
from gcloud.openapi.schema import AnnotationAutoSchema
from gcloud.taskflow3.models import TaskFlowInstance, TaskFlowRelation

logger = logging.getLogger("root")


@check_is_superuser()
def delete_cache_key(request, key):
    cache.delete(key)
    return JsonResponse({"result": True, "code": err_code.SUCCESS.code, "data": "success"})


@check_is_superuser()
def get_cache_key(request, key):
    data = cache.get(key)
    return JsonResponse({"result": True, "code": err_code.SUCCESS.code, "data": data})


@check_is_superuser()
def get_settings(request):
    data = {s: getattr(settings, s) for s in dir(settings)}
    return JsonResponse({"result": True, "code": err_code.SUCCESS.code, "data": data})


@check_is_superuser()
def migrate_pipeline_parent_data(request):
    """
    @summary: 将 pipeline 的 schedule_parent_data 从 _backend(redis) 迁移到 _candidate_backend(mysql)
    @param request:
    @return:
    """
    migrate_pipeline_parent_data_task.apply_async()
    return JsonResponse({"reuslt": True, "data": None, "message": "migrte start."})


@check_is_superuser()
def upsert_iam_system_provider_config(request):
    """
    重新注册iam的第三方系统资源信息
    """
    new_resource_host = request.GET.get("new_resource_host")
    provider_config = {"host": new_resource_host or env.BK_IAM_RESOURCE_API_HOST, "auth": "basic"}
    data = {"provider_config": provider_config}
    iam_client = Client(
        env.BKAPP_SOPS_IAM_APP_CODE,
        env.BKAPP_SOPS_IAM_APP_SECRET_KEY,
        settings.BK_IAM_INNER_HOST,
        settings.BK_PAAS_ESB_HOST,
    )
    ok, message = iam_client.update_system(system_id=env.BKAPP_BK_IAM_SYSTEM_ID, data=data)
    return JsonResponse({"result": ok, "data": None, "message": message})


@swagger_auto_schema(method="post", auto_schema=AnnotationAutoSchema)
@api_view(["POST"])
@check_is_superuser()
def batch_insert_project_based_component(request):
    """
    给某业务添加一批基于业务的插件

    body: data
    {
        "project_id(optional)": "项目 ID",
        "project_ids(optional)": "项目 ID 列表(list)",
        "component_codes(required)": "插件code列表(list)"
    }
    """
    project_ids = []
    if "project_id" in request.data:
        project_ids.append(request.data["project_id"])
    if "project_ids" in request.data:
        project_ids.extend(request.data["project_ids"])

    component_codes = request.data.get("component_codes")

    existing_unique_keys = {
        f"{component.project_id}-{component.component_code}"
        for component in ProjectBasedComponent.objects.filter(
            project_id__in=project_ids, component_code__in=component_codes
        )
    }

    components = [
        ProjectBasedComponent(project_id=str(project_id), component_code=component_code)
        for project_id, component_code in product(set(project_ids), set(component_codes))
        if f"{project_id}-{component_code}" not in existing_unique_keys
    ]
    create_results = ProjectBasedComponent.objects.bulk_create(components)
    return JsonResponse({"result": True, "data": create_results, "message": ""})


@swagger_auto_schema(method="post", auto_schema=AnnotationAutoSchema)
@api_view(["POST"])
@check_is_superuser()
def batch_delete_project_based_component(request):
    """
    删除某个业务的一批基于业务的插件

    body: data
    {
        "project_id(optional)": "项目 ID",
        "project_ids(optional)": "项目 ID 列表(list)",
        "component_codes(required)": "插件code列表(list)"
    }
    """
    project_ids = []
    if "project_id" in request.data:
        project_ids.append(request.data["project_id"])
    if "project_ids" in request.data:
        project_ids.extend(request.data["project_ids"])

    # to string
    project_ids = [str(project_id) for project_id in project_ids]
    component_codes = request.data.get("component_codes")
    deleted, rows_count = ProjectBasedComponent.objects.filter(
        project_id__in=set(project_ids), component_code__in=set(component_codes)
    ).delete()
    return JsonResponse({"result": True, "data": [], "message": f"deleted -> {deleted}, rows_count -> {rows_count}"})


@swagger_auto_schema(method="post", auto_schema=AnnotationAutoSchema)
@api_view(["POST"])
@check_is_superuser()
def batch_revoke_task(request):
    """
    批量 终止某批任务，并终止该任务下面正在执行的节点
    body: data
    {
        "project_id": 任务 id
        "task_id(optional)": "任务 id ",
        "task_ids(optional)": "任务 ID 列表(list)",
    }
    """

    task_ids = []
    if "task_id" in request.data:
        task_ids.append(request.data["task_id"])
    if "task_ids" in request.data:
        task_ids.extend(request.data["task_ids"])

    project_id = request.data.get("project_id")
    if not project_id:
        return JsonResponse({"result": False, "data": [], "message": "操作失败，project_id 不能为空"})

    tasks = TaskFlowInstance.objects.filter(id__in=task_ids, project_id=project_id, is_deleted=False)

    logger.info(
        "start batch revoke task, task_count={}, tasks={}, project_id={}".format(
            len(task_ids), task_ids[0:100], project_id
        )
    )

    revoke_failed_tasks = []

    for task in tasks:
        try:
            # 终止主任务
            force_tasks([task], request.user.username)
            # 终止子任务
            task_ids = TaskFlowRelation.objects.filter(root_task_id=task.id).values_list("task_id", flat=True)
            sub_tasks = TaskFlowInstance.objects.filter(id__in=task_ids, project_id=project_id, is_deleted=False)
            force_tasks(sub_tasks, request.user.username)
        except Exception as e:
            logger.exception("revoked task failed, err={}".format(e))
            revoke_failed_tasks.append(task.id)
    if revoke_failed_tasks:
        return JsonResponse({"result": False, "data": [], "message": "存在终止异常的任务 = {}".format(revoke_failed_tasks)})

    return JsonResponse({"result": True, "data": [], "message": f"revoked -> {tasks.count()}"})


@check_is_superuser()
def get_enabled_periodic_task(request):
    is_send_notify = True if request.GET.get("is_send_notify", "false") == "true" else False
    data = scan_periodic_task(is_send_notify)
    return JsonResponse({"result": True, "code": err_code.SUCCESS.code, "data": data})
