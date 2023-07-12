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

from django.test import TestCase
from django.utils.timezone import now
from mock import MagicMock, patch

from gcloud.clocked_task.models import ClockedTask
from gcloud.clocked_task.tasks import clocked_task_start
from gcloud.constants import TaskCreateMethod
from gcloud.tests.mock_settings import *  # noqa


class ClockedTaskStartTestCase(TestCase):
    def test_clocked_task_not_exist(self):
        clocked_task_start(-1)

    def test_success(self):
        task_params = {
            "description": "desc",
            "constants": "constants",
            "exclude_task_nodes_id": "exclude_task_nodes_id",
            "simplify_vars": "simplify_vars",
        }
        task = ClockedTask.objects.create(
            project_id=1,
            task_name="task_name",
            template_id=3,
            template_name="name",
            creator="tester",
            plan_start_time=now(),
            task_params=json.dumps(task_params),
        )

        timestamp = "20220907000000"
        project = MagicMock()
        project.id = 1
        Project = MagicMock()
        Project.objects.get = MagicMock(return_value=project)
        Project.objects.get_timezone_based_timestamp = MagicMock(return_value=timestamp)

        task_template = MagicMock()
        task_template.pipeline_tree = MagicMock()
        TaskTemplate = MagicMock()
        TaskTemplate.objects.select_related().get = MagicMock(return_value=task_template)

        taskflow_instance = MagicMock()
        taskflow_instance.id = 123
        TaskFlowInstance = MagicMock()
        TaskFlowInstance.objects.create = MagicMock(return_value=taskflow_instance)
        TaskFlowInstance.objects.create_pipeline_instance_exclude_task_nodes = MagicMock(return_value="data")

        arn_creator = MagicMock()
        AutoRetryNodeStrategyCreator = MagicMock(return_value=arn_creator)

        project_patcher = patch(GCLOUD_CLOCKED_TASK_TASKS_PROJECT, Project)
        task_template_patcher = patch(GCLOUD_CLOCKED_TASK_TASKS_TASK_TEMPLATE, TaskTemplate)
        taskflow_instance_patcher = patch(GCLOUD_CLOCKED_TASK_TASKS_TASKFLOW_INSTANCE, TaskFlowInstance)
        arn_creator_patcher = patch(GCLOUD_CLOCKED_TASK_TASKS_ARN_CREATOR, AutoRetryNodeStrategyCreator)

        project_patcher.start()
        task_template_patcher.start()
        taskflow_instance_patcher.start()
        arn_creator_patcher.start()

        clocked_task_start(task.id)

        project_patcher.stop()
        task_template_patcher.stop()
        taskflow_instance_patcher.stop()
        arn_creator_patcher.stop()

        Project.objects.get.assert_called_once_with(id=task.project_id)
        TaskTemplate.objects.select_related().get.assert_called_once_with(
            id=task.template_id, project_id=project.id, is_deleted=False
        )
        TaskFlowInstance.objects.create_pipeline_instance_exclude_task_nodes.assert_called_once_with(
            task_template,
            {
                "name": f"{task.task_name}_{timestamp}",
                "creator": task.creator,
                "description": task_params.get("description", ""),
            },
            task_params.get("constants"),
            task_params.get("exclude_task_nodes_id"),
            task_params.get("simplify_vars"),
            task_template.pipeline_tree,
        )
        TaskFlowInstance.objects.create.assert_called_once_with(
            project=project,
            pipeline_instance="data",
            category=task_template.category,
            template_id=task.template_id,
            template_source=task.template_source,
            create_method=TaskCreateMethod.CLOCKED.value,
            create_info=task.id,
            flow_type="common",
            current_flow="execute_task",
            engine_ver=2,
        )
        task.refresh_from_db()
        self.assertEqual(task.task_id, taskflow_instance.id)
        AutoRetryNodeStrategyCreator.assert_called_once_with(
            taskflow_id=taskflow_instance.id, root_pipeline_id=taskflow_instance.pipeline_instance.instance_id
        )
        arn_creator.batch_create_strategy.assert_called_once_with(taskflow_instance.pipeline_instance.execution_data)
