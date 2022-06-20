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

import datetime


from django.test import TestCase
from mock.mock import MagicMock


from gcloud.taskflow3.models import TaskFlowInstance
from gcloud.tests.mock import mock
from gcloud.tests.mock_settings import TASKFLOW_STATISTICS_FILTER, PIPELINE_INSTANCE_FILTER, PROJECT_FILTER
from gcloud.utils.dates import format_datetime

TEST_TOTAL = 15
TEST_PAGE = 1
TEST_LIMIT = 10
TEST_PROJ_ID = 12345
TEST_CREATE_TIME = datetime.datetime.now()
TEST_TASK_INSTANCE_ID_LIST = [i for i in range(1, TEST_TOTAL + 1)]
TEST_TASKFLOW = MagicMock()
TEST_TASKFLOW.count = MagicMock(return_value=TEST_TOTAL)
TEST_TASKFLOW.values_list = MagicMock(return_value=TEST_TASK_INSTANCE_ID_LIST)
TEST_TASKFLOW_STATISTICS_DATA = [
    {
        "instance_id": i,
        "task_instance_id": i,
        "project_id": TEST_PROJ_ID,
        "category": "test_category",
        "create_time": TEST_CREATE_TIME,
        "creator": "test_creator",
        "elapsed_time": "elapsed_time",
        "atom_total": i,
        "subprocess_total": i,
        "gateways_total": i,
        "create_method": "test_create_method",
    }
    for i in range(1, TEST_LIMIT + 1)
]
TEST_TASKFLOW_STATISTICS = MagicMock(return_value=TEST_TASKFLOW_STATISTICS_DATA)
TEST_INSTANCE_NAMEDATA = [(i, "test_instance") for i in range(1, TEST_LIMIT + 1)]
TEST_PROJECT_NAMEDATA = [(TEST_PROJ_ID, "test_proj")]
TEST_GROUPS = [
    {
        "instance_id": i,
        "instance_name": dict(TEST_INSTANCE_NAMEDATA)[i],
        "project_id": TEST_PROJ_ID,
        "project_name": dict(TEST_PROJECT_NAMEDATA)[TEST_PROJ_ID],
        "category": "test_category",
        "create_time": format_datetime(TEST_CREATE_TIME),
        "creator": "test_creator",
        "elapsed_time": "elapsed_time",
        "atom_total": i,
        "subprocess_total": i,
        "gateways_total": i,
        "create_method": "test_create_method",
    }
    for i in range(1, TEST_LIMIT + 1)
]


class MockTaskflowStatistics(MagicMock):
    def values(self, *args, **kwargs):
        return TEST_TASKFLOW_STATISTICS_DATA


class MockInstanceDict(MagicMock):
    def values_list(self, *args, **kwargs):
        return TEST_INSTANCE_NAMEDATA


class MockProjectDict(MagicMock):
    def values_list(self, *args, **kwargs):
        return TEST_PROJECT_NAMEDATA


class TestGroupByInstanceNode(TestCase):
    def test_group_by_instance_node(self):
        with mock.patch(TASKFLOW_STATISTICS_FILTER, MockTaskflowStatistics()) as mock_statistics_filter:
            with mock.patch(PIPELINE_INSTANCE_FILTER, MockInstanceDict()) as mock_instance_dict:
                with mock.patch(PROJECT_FILTER, MockProjectDict()) as mock_project_dict:
                    total, groups = TaskFlowInstance.objects.group_by_instance_node(
                        taskflow=TEST_TASKFLOW, filters=None, page=TEST_PAGE, limit=TEST_LIMIT
                    )
                    mock_statistics_filter.assert_called_once_with(task_instance_id__in=TEST_TASK_INSTANCE_ID_LIST)
                    mock_instance_dict.assert_called_once_with(id__in=TEST_TASK_INSTANCE_ID_LIST[0:TEST_LIMIT])
                    mock_project_dict.assert_called_once_with(id__in=[TEST_PROJ_ID for i in range(TEST_LIMIT)])
                    self.assertEqual(total, TEST_TOTAL)
                    self.assertEqual(groups, TEST_GROUPS)
