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

from django.test import TestCase

from gcloud.tests.mock import *  # noqa
from gcloud.tests.mock_settings import *  # noqa
from gcloud.tests.test_data import TEST_STATUS_TREE, TEST_EXECUTION_DATA
from gcloud.analysis_statistics.tasks import pipeline_archive_statistics_task

mock.mock._magics.add("__round__")

TEST_TASK_INSTANCE_ID = 1
TEST_PIPELINE_INSTANCE = MockPipelineInstance({"execution_data": TEST_EXECUTION_DATA})


class TestPipelineArchiveStatisticsTask(TestCase):
    @mock.patch(PIPELINE_INSTANCE_GET, MagicMock(return_value=TEST_PIPELINE_INSTANCE))
    @mock.patch(TASKINSTANCE_GET, MagicMock(return_value=MockTaskFlowInstance()))
    def test_get_status_tree_fail_case(self):
        result = pipeline_archive_statistics_task(TEST_TASK_INSTANCE_ID)
        self.assertFalse(result)

    @mock.patch(PIPELINE_INSTANCE_GET, MagicMock(return_value=TEST_PIPELINE_INSTANCE))
    @mock.patch(TASKINSTANCE_GET, MagicMock(return_value=MockTaskFlowInstance()))
    @mock.patch(TASKFLOW_MODEL_TASK_COMMAND_DISPATCHER, MagicMock(return_value=MockTaskCommandDispatcher()))
    @mock.patch(TASKFLOW_MODEL_TASK_COMMAND_DISPATCHER_GET_STATUS, MagicMock(return_value=TEST_STATUS_TREE))
    @mock.patch(TASKFLOWEXECUTEDNODE_STATISTICS_FILTER, MagicMock(return_value=MockQuerySet()))
    @mock.patch(TASKTEMPLATE_GET, MagicMock(return_value=MockTaskTemplate()))
    def test_task_success(self):
        result = pipeline_archive_statistics_task(TEST_TASK_INSTANCE_ID)
        self.assertTrue(result)
