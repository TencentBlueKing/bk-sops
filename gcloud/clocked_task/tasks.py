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
import json
import logging

from celery import task
from django.db import transaction
from pipeline.models import MAX_LEN_OF_NAME

from gcloud.clocked_task.models import ClockedTask
from gcloud.constants import (
    CLOCKED_TASK_START_FAILED,
    CLOCKED_TASK_STARTED,
    TaskCreateMethod,
)
from gcloud.core.models import EngineConfig, Project
from gcloud.shortcuts.message import send_clocked_task_message
from gcloud.taskflow3.domains.auto_retry import AutoRetryNodeStrategyCreator
from gcloud.taskflow3.models import TaskFlowInstance, TimeoutNodeConfig
from gcloud.tasktmpl3.models import TaskTemplate
from pipeline_web.preview_base import PipelineTemplateWebPreviewer

logger = logging.getLogger("celery")


def parse_exclude_task_nodes_id_from_params(pipeline_tree, task_params):
    if task_params.get("exclude_task_nodes_id"):
        return task_params["exclude_task_nodes_id"]
    exclude_task_nodes_id = []
    if task_params.get("appoint_task_nodes_id"):
        exclude_task_nodes_id = PipelineTemplateWebPreviewer.get_template_exclude_task_nodes_with_appoint_nodes(
            pipeline_tree, task_params["appoint_task_nodes_id"]
        )
    elif task_params.get("template_schemes_id"):
        exclude_task_nodes_id = PipelineTemplateWebPreviewer.get_template_exclude_task_nodes_with_schemes(
            pipeline_tree, task_params["template_schemes_id"], check_schemes_exist=True
        )
    return exclude_task_nodes_id


@task
def clocked_task_start(clocked_task_id, *args, **kwargs):
    try:
        clocked_task = ClockedTask.objects.get(id=clocked_task_id)
    except ClockedTask.DoesNotExist:
        # task has been deleted
        logger.warning(f"[clocked_task_start] clocked task {clocked_task_id} not found, may be deleted.")
        return
    try:
        timestamp = Project.objects.get_timezone_based_timestamp(project_id=clocked_task.project_id)
        task_name = f"{clocked_task.task_name}_{timestamp}"[:MAX_LEN_OF_NAME]
        task_params = json.loads(clocked_task.task_params)
        pipeline_instance_kwargs = {
            "name": task_name,
            "creator": clocked_task.creator,
            "description": task_params.get("description", ""),
        }
        project = Project.objects.get(id=clocked_task.project_id)
        template = TaskTemplate.objects.select_related("pipeline_template").get(
            id=clocked_task.template_id, project_id=project.id, is_deleted=False
        )
        pipeline_tree = template.pipeline_tree
        exclude_task_nodes_id = parse_exclude_task_nodes_id_from_params(pipeline_tree, task_params)
        with transaction.atomic():
            data = TaskFlowInstance.objects.create_pipeline_instance_exclude_task_nodes(
                template,
                pipeline_instance_kwargs,
                task_params.get("constants"),
                exclude_task_nodes_id,
                task_params.get("simplify_vars"),
                pipeline_tree,
            )
            taskflow_instance = TaskFlowInstance.objects.create(
                project=project,
                pipeline_instance=data,
                category=template.category,
                template_id=clocked_task.template_id,
                template_source=clocked_task.template_source,
                create_method=TaskCreateMethod.CLOCKED.value,
                create_info=clocked_task.id,
                flow_type="common",
                current_flow="execute_task",
                engine_ver=EngineConfig.objects.get_engine_ver(
                    project_id=project.id,
                    template_id=clocked_task.template_id,
                    template_source=clocked_task.template_source,
                ),
            )
            ClockedTask.objects.filter(id=clocked_task_id).update(
                task_id=taskflow_instance.id, state=CLOCKED_TASK_STARTED
            )

            # crete auto retry strategy
            arn_creator = AutoRetryNodeStrategyCreator(
                taskflow_id=taskflow_instance.id, root_pipeline_id=taskflow_instance.pipeline_instance.instance_id
            )
            arn_creator.batch_create_strategy(taskflow_instance.pipeline_instance.execution_data)

            # create timeout config
            TimeoutNodeConfig.objects.batch_create_node_timeout_config(
                taskflow_id=taskflow_instance.id,
                root_pipeline_id=taskflow_instance.pipeline_instance.instance_id,
                pipeline_tree=taskflow_instance.pipeline_instance.execution_data,
            )

        taskflow_instance.task_action("start", clocked_task.creator)
    except Exception as ex:
        logger.exception("[clocked_task_start] task create error")
        ClockedTask.objects.filter(id=clocked_task_id).update(state=CLOCKED_TASK_START_FAILED)
        send_clocked_task_message(clocked_task, str(ex))
