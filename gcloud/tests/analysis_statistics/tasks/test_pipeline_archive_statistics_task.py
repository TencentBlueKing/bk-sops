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

from gcloud.tests.mock import *  # noqa
from gcloud.tests.mock_settings import *  # noqa
from gcloud.tests.test_data import TEST_STATUS_TREE, TEST_EXECUTION_DATA
from gcloud.analysis_statistics.tasks import pipeline_archive_statistics_task
from gcloud.analysis_statistics.models import TaskflowExecutedNodeStatistics
from gcloud.taskflow3.models import TaskCommandDispatcher, TaskFlowInstance

mock.mock._magics.add("__round__")

TEST_TASK_INSTANCE_ID = 1
TEST_PIPELINE_INSTANCE = MockPipelineInstance(execution_data=TEST_EXECUTION_DATA)

taskflow = MockTaskFlowInstance(pipeline_instance=TEST_PIPELINE_INSTANCE, id=1)


class TestPipelineArchiveStatisticsTask(TestCase):
    @mock.patch(TASKINSTANCE_GET, MagicMock(return_value=taskflow))
    @mock.patch(TASKFLOW_MODEL_TASK_COMMAND_DISPATCHER_GET_STATUS, MagicMock(return_value=TEST_STATUS_TREE))
    @mock.patch(TASKFLOWEXECUTEDNODE_STATISTICS_FILTER, MagicMock(return_value=MockQuerySet()))
    @mock.patch(TASKTEMPLATE_GET, MagicMock(return_value=MockTaskTemplate()))
    def test_task_success(self):
        result = pipeline_archive_statistics_task(TEST_TASK_INSTANCE_ID)

        TaskFlowInstance.objects.get.assert_called_once_with(pipeline_instance__instance_id=TEST_TASK_INSTANCE_ID)
        TaskCommandDispatcher.get_task_status.assert_called_once_with()
        TaskflowExecutedNodeStatistics.objects.filter.assert_called_once_with(instance_id=taskflow.pipeline_instance.id)
        self.assertTrue(result)
