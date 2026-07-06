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

from django.test import TestCase

from gcloud.analysis_statistics.models import TaskflowStatistics
from gcloud.analysis_statistics.tasks import taskflowinstance_post_save_statistics_task
from gcloud.taskflow3.models import TaskFlowInstance
from gcloud.tasktmpl3.models import TaskTemplate
from gcloud.tests.mock import *  # noqa
from gcloud.tests.mock_settings import *  # noqa

mock.mock._magics.add("__round__")

TEST_TASK_INSTANCE_ID = 1

MOCK_COUNT_TREE_NODES = "gcloud.analysis_statistics.tasks.count_pipeline_tree_nodes"

pipeline = MockPipelineInstance()
taskflow = MockTaskFlowInstance(id=1, pipeline_instance=pipeline)
tasktmpl = MockTaskTemplate(id=1)


class TestTaskflowinstancePostSaveStatistics(TestCase):
    @mock.patch(TASKINSTANCE_GET, MagicMock(return_value=taskflow))
    @mock.patch(TASKTEMPLATE_GET, MagicMock(return_value=tasktmpl))
    @mock.patch(CALCULATE_ELAPSED_TIME, MagicMock(return_value=0))
    @mock.patch(MOCK_COUNT_TREE_NODES, MagicMock(return_value=(1, 1, 1)))
    @mock.patch(TASKFLOW_STATISTICS_CREATE, MagicMock(return_value=MockQuerySet()))
    def test_task_success_case_with_created(self):
        kwargs = {
            "task_instance_id": TEST_TASK_INSTANCE_ID,
            "instance_id": pipeline.id,
            "project_id": taskflow.project.id,
            "category": tasktmpl.category,
            "template_id": tasktmpl.pipeline_template.id,
            "task_template_id": tasktmpl.id,
            "creator": pipeline.creator,
            "create_time": pipeline.create_time,
            "start_time": pipeline.start_time,
            "finish_time": pipeline.finish_time,
            "elapsed_time": 0,
            "create_method": taskflow.create_method,
            "gateways_total": 1,
            "subprocess_total": 1,
            "atom_total": 1,
        }
        result = taskflowinstance_post_save_statistics_task(TEST_TASK_INSTANCE_ID, True)
        TaskFlowInstance.objects.get.assert_called_once_with(id=taskflow.id)
        TaskTemplate.objects.get.assert_called_once_with(id=tasktmpl.id)
        TaskflowStatistics.objects.create.assert_called_once_with(**kwargs)
        self.assertTrue(result)

    @mock.patch(TASKINSTANCE_GET, MagicMock(return_value=taskflow))
    @mock.patch(TASKTEMPLATE_GET, MagicMock(return_value=tasktmpl))
    @mock.patch(CALCULATE_ELAPSED_TIME, MagicMock(return_value=0))
    @mock.patch(MOCK_COUNT_TREE_NODES, MagicMock(return_value=(1, 1, 1)))
    @mock.patch(TASKFLOW_STATISTICS_FILTER, MagicMock(return_value=MockQuerySet()))
    def test_task_success_case_without_created(self):
        kwargs = {
            "instance_id": pipeline.id,
            "project_id": taskflow.project.id,
            "category": tasktmpl.category,
            "template_id": tasktmpl.pipeline_template.id,
            "task_template_id": tasktmpl.id,
            "creator": pipeline.creator,
            "create_time": pipeline.create_time,
            "start_time": pipeline.start_time,
            "finish_time": pipeline.finish_time,
            "elapsed_time": 0,
            "create_method": taskflow.create_method,
            "gateways_total": 1,
            "subprocess_total": 1,
            "atom_total": 1,
        }
        result = taskflowinstance_post_save_statistics_task(TEST_TASK_INSTANCE_ID, False)
        TaskFlowInstance.objects.get.assert_called_once_with(id=taskflow.id)
        TaskTemplate.objects.get.assert_called_once_with(id=tasktmpl.id)
        TaskflowStatistics.objects.filter.assert_called_once_with(task_instance_id=TEST_TASK_INSTANCE_ID)
        TaskflowStatistics.objects.filter.return_value.update.assert_called_once_with(**kwargs)
        self.assertTrue(result)
