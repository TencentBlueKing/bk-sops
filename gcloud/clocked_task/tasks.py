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
import json
import logging

from celery import task
from django.db import transaction

from gcloud.clocked_task.models import ClockedTask
from gcloud.core.models import Project, EngineConfig
from gcloud.taskflow3.models import TaskFlowInstance
from gcloud.tasktmpl3.models import TaskTemplate

logger = logging.getLogger("celery")


@task
def clocked_task_start(clocked_task_id, *args, **kwargs):
    try:
        clocked_task = ClockedTask.objects.get(id=clocked_task_id)
    except ClockedTask.DoesNotExist:
        # task has been deleted
        logger.warning(f"[clocked_task_start] clocked task {clocked_task_id} not found, may be deleted.")
        return

    task_params = json.loads(clocked_task.task_params)
    pipeline_instance_kwargs = {
        "name": clocked_task.task_name,
        "creator": clocked_task.creator,
        "description": task_params.get("description", ""),
    }
    try:
        with transaction.atomic():
            project = Project.objects.get(id=clocked_task.project_id)
            template = TaskTemplate.objects.select_related("pipeline_template").get(
                id=clocked_task.template_id, project_id=project.id, is_deleted=False
            )
            data = TaskFlowInstance.objects.create_pipeline_instance_exclude_task_nodes(
                template,
                pipeline_instance_kwargs,
                task_params.get("constants"),
                task_params.get("exclude_task_nodes_id"),
                task_params.get("simplify_vars"),
            )
            taskflow_instance = TaskFlowInstance.objects.create(
                project=project,
                pipeline_instance=data,
                category=template.category,
                template_id=clocked_task.template_id,
                template_source=clocked_task.template_source,
                create_method="clocked",
                create_info=clocked_task.id,
                flow_type="common",
                current_flow="execute_task",
                engine_ver=EngineConfig.objects.get_engine_ver(
                    project_id=project.id,
                    template_id=clocked_task.template_id,
                    template_source=clocked_task.template_source,
                ),
            )
            ClockedTask.objects.filter(id=clocked_task_id).update(task_id=taskflow_instance.id)
        taskflow_instance.task_action("start", clocked_task.creator)
    except Exception:
        logger.exception("[clocked_task_start] task create error")
