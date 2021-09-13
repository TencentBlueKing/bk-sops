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

from pipeline.utils.uniqid import node_uniqid

from gcloud.tests.mock import MockTaskFlowInstance, mock, MagicMock, MockQuerySet
from gcloud.tests.mock_settings import TASKTEMPLATE_GET
from gcloud.analysis_statistics.tasks import recursive_collect_components_execution

TEST_STATUS_TREE = (2, 0, 0)
TEST_PROJECT_ID = "2"  # do not change this to non number
TEST_ID_LIST = [node_uniqid() for i in range(10)]
TEST_ACTIVIES = {
    TEST_ID_LIST[3]: {
        "id": TEST_ID_LIST[3],
        "type": "ServiceActivity",
        "name": "first_task",
        "incoming": TEST_ID_LIST[5],
        "outgoing": TEST_ID_LIST[6],
        "optional": True,
        "component": {
            "code": "test",
            "data": {
                "input_test": {"hook": False, "value": "${custom_key1}"},
                "radio_test": {"hook": False, "value": "1"},
            },
        },
    },
    TEST_ID_LIST[4]: {
        "id": TEST_ID_LIST[4],
        "type": "ServiceActivity",
        "name": "first_task",
        "incoming": TEST_ID_LIST[6],
        "outgoing": TEST_ID_LIST[7],
        "optional": True,
        "component": {
            "code": "test",
            "data": {
                "input_test": {"hook": True, "value": "${custom_key2}"},
                "radio_test": {"hook": False, "value": "2"},
            },
        },
    },
}
TEST_TASK_INSTANCE = MockTaskFlowInstance()


class TestRecursiveCollectComponentsExecution(TestCase):
    @mock.patch(TASKTEMPLATE_GET, MagicMock(return_value=MockQuerySet()))
    def test_recursive_collect_components_execution(self):
        assert_data = []
        data = recursive_collect_components_execution(TEST_ACTIVIES, TEST_STATUS_TREE, TEST_TASK_INSTANCE)
        self.assertEqual(assert_data, data)
