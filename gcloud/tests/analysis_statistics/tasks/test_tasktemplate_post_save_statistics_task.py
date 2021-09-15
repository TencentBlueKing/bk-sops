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
from gcloud.tests.test_data import *  # noqa
from gcloud.analysis_statistics.tasks import tasktemplate_post_save_statistics_task

mock.mock._magics.add("__round__")

TEST_TASK_INSTANCE_ID = 1
TEST_COMPONENTS = [
    {"subprocess_stack": "[1,1,1]", "component_code": "component_code", "node_id": "node_id", "version": "version"}
]
TEST_COUNT_PIPELINE_TREE_NODES = (1, 1, 1)


class MockTemplateNodeStatisticsQuerySet(MockQuerySet):
    def values(self, *args, **kwargs):
        return TEST_COMPONENTS


class TestTaskTemplatePostSaveStatisticsTask(TestCase):
    @mock.patch(TASKTEMPLATE_GET, MagicMock(return_value=MockTaskTemplate()))
    @mock.patch(TEMPLATENODE_STATISTICS_FILTER, MagicMock(return_value=MockTemplateNodeStatisticsQuerySet()))
    @mock.patch(TEMPLATENODE_STATISTICS_BULK_CREATE, MagicMock(return_value=MockQuerySet()))
    @mock.patch(COUNT_PIPELINE_TREE_NODES, MagicMock(return_value=TEST_COUNT_PIPELINE_TREE_NODES))
    @mock.patch(TEMPLATE_STATISTICS_UPDATE_OR_CREATE, MagicMock(return_value=MockQuerySet()))
    def test_task_success_case(self):
        result = tasktemplate_post_save_statistics_task(TEST_TASK_INSTANCE_ID)
        self.assertTrue(result)
