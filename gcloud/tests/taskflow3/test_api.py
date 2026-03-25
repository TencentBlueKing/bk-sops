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

from copy import deepcopy

from django.test import TestCase, Client

from pipeline.utils.uniqid import node_uniqid

from gcloud.tests.mock import *  # noqa
from gcloud.tests.mock_settings import *  # noqa
from gcloud.taskflow3.apis.django import api


TEST_PROJECT_ID = "2"  # do not change this to non number
TEST_ID_LIST = [node_uniqid() for i in range(10)]
TEST_PIPELINE_TREE = {
    "id": TEST_ID_LIST[0],
    "name": "name",
    "start_event": {
        "id": TEST_ID_LIST[1],
        "name": "start",
        "type": "EmptyStartEvent",
        "incoming": None,
        "outgoing": TEST_ID_LIST[5],
    },
    "end_event": {
        "id": TEST_ID_LIST[2],
        "name": "end",
        "type": "EmptyEndEvent",
        "incoming": TEST_ID_LIST[7],
        "outgoing": None,
    },
    "activities": {
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
    },
    "flows": {  # 存放该 Pipeline 中所有的线
        TEST_ID_LIST[5]: {"id": TEST_ID_LIST[5], "source": TEST_ID_LIST[1], "target": TEST_ID_LIST[3]},
        TEST_ID_LIST[6]: {"id": TEST_ID_LIST[6], "source": TEST_ID_LIST[3], "target": TEST_ID_LIST[4]},
        TEST_ID_LIST[7]: {"id": TEST_ID_LIST[7], "source": TEST_ID_LIST[4], "target": TEST_ID_LIST[2]},
    },
    "gateways": {},  # 这里存放着网关的详细信息
    "constants": {
        "${custom_key1}": {
            "index": 0,
            "name": "input1",
            "key": "${custom_key1}",
            "desc": "",
            "validation": "^.*$",
            "show_type": "show",
            "value": "value1",
            "source_type": "custom",
            "source_tag": "",
            "source_info": {},
            "custom_type": "input",
        },
        "${custom_key2}": {
            "index": 1,
            "name": "input2",
            "key": "${custom_key2}",
            "desc": "",
            "validation": "^.*$",
            "show_type": "show",
            "value": "value1",
            "source_type": "custom",
            "source_tag": "",
            "source_info": {},
            "custom_type": "input",
        },
    },
    "outputs": ["${custom_key1}"],
}


class APITest(TestCase):
    def setUp(self):
        self.PREVIEW_TASK_TREE_URL = "/taskflow/api/preview_task_tree/{biz_cc_id}/"
        self.client = Client()

    @mock.patch("gcloud.taskflow3.apis.django.api.JsonResponse", MockJsonResponse())
    @mock.patch("gcloud.taskflow3.apis.django.api.TaskFlowInstance.objects.filter")
    def test_preview_task_tree__constants_not_referred(self, mock_filter):
        mock_filter.return_value.order_by.return_value.only.return_value.first.return_value = None

        with mock.patch(
            TASKTEMPLATE_GET, MagicMock(return_value=MockBaseTemplate(id=1, pipeline_tree=deepcopy(TEST_PIPELINE_TREE)))
        ):
            data1 = {
                "template_source": "project",
                "template_id": 1,
                "version": "test_version",
                "exclude_task_nodes_id": [TEST_ID_LIST[3]],
            }
            result = api.preview_task_tree(MockJsonBodyRequest("POST", data1), TEST_PROJECT_ID)
            self.assertTrue(result["result"])
            self.assertEqual(list(result["data"]["constants_not_referred"].keys()), ["${custom_key1}"])

        with mock.patch(
            TASKTEMPLATE_GET, MagicMock(return_value=MockBaseTemplate(id=1, pipeline_tree=deepcopy(TEST_PIPELINE_TREE)))
        ):
            data2 = {
                "template_source": "project",
                "template_id": 1,
                "version": "test_version",
                "exclude_task_nodes_id": [TEST_ID_LIST[4]],
            }
            result = api.preview_task_tree(MockJsonBodyRequest("POST", data2), TEST_PROJECT_ID)
            self.assertTrue(result["result"])
            self.assertEqual(list(result["data"]["constants_not_referred"].keys()), ["${custom_key2}"])

        with mock.patch(
            TASKTEMPLATE_GET, MagicMock(return_value=MockBaseTemplate(id=1, pipeline_tree=deepcopy(TEST_PIPELINE_TREE)))
        ):
            data3 = {
                "template_source": "project",
                "template_id": 1,
                "version": "test_version",
                "exclude_task_nodes_id": [],
            }
            result = api.preview_task_tree(MockJsonBodyRequest("POST", data3), TEST_PROJECT_ID)
            self.assertTrue(result["result"])
            self.assertEqual(list(result["data"]["constants_not_referred"].keys()), [])

        with mock.patch(
            TASKTEMPLATE_GET, MagicMock(return_value=MockBaseTemplate(id=1, pipeline_tree=deepcopy(TEST_PIPELINE_TREE)))
        ):
            data4 = {
                "template_source": "project",
                "template_id": 1,
                "version": "test_version",
                "exclude_task_nodes_id": [TEST_ID_LIST[3], TEST_ID_LIST[4]],
            }
            result = api.preview_task_tree(MockJsonBodyRequest("POST", data4), TEST_PROJECT_ID)
            self.assertTrue(result["result"])
            self.assertEqual(
                list(result["data"]["constants_not_referred"].keys()), ["${custom_key1}", "${custom_key2}"]
            )

    @mock.patch("gcloud.taskflow3.apis.django.api.JsonResponse", MockJsonResponse())
    @mock.patch("gcloud.taskflow3.apis.django.api.TaskFlowInstance.objects.filter")
    def test_preview_task_tree__last_execution_id_exists(self, mock_filter):
        mock_task = MagicMock()
        mock_task.id = 999
        mock_filter.return_value.order_by.return_value.only.return_value.first.return_value = mock_task

        with mock.patch(
            TASKTEMPLATE_GET, MagicMock(return_value=MockBaseTemplate(id=1, pipeline_tree=deepcopy(TEST_PIPELINE_TREE)))
        ):
            data = {
                "template_source": "project",
                "template_id": "1",
                "version": "test_version",
                "exclude_task_nodes_id": [],
            }
            result = api.preview_task_tree(MockJsonBodyRequest("POST", data), TEST_PROJECT_ID)
            self.assertTrue(result["result"])
            self.assertEqual(result["data"]["last_execution_id"], 999)

    @mock.patch("gcloud.taskflow3.apis.django.api.JsonResponse", MockJsonResponse())
    @mock.patch("gcloud.taskflow3.apis.django.api.TaskFlowInstance.objects.filter")
    def test_preview_task_tree__last_execution_id_none(self, mock_filter):
        mock_filter.return_value.order_by.return_value.only.return_value.first.return_value = None

        with mock.patch(
            TASKTEMPLATE_GET, MagicMock(return_value=MockBaseTemplate(id=1, pipeline_tree=deepcopy(TEST_PIPELINE_TREE)))
        ):
            data = {
                "template_source": "project",
                "template_id": "1",
                "version": "test_version",
                "exclude_task_nodes_id": [],
            }
            result = api.preview_task_tree(MockJsonBodyRequest("POST", data), TEST_PROJECT_ID)
            self.assertTrue(result["result"])
            self.assertIsNone(result["data"]["last_execution_id"])

    @mock.patch("gcloud.taskflow3.apis.django.api.JsonResponse", MockJsonResponse())
    @mock.patch("gcloud.taskflow3.apis.django.api.TaskFlowInstance.objects.filter")
    def test_last_execution_constants__success(self, mock_filter):
        mock_pipeline_instance = MagicMock()
        mock_pipeline_instance.execution_data = {
            "constants": {
                "${ip}": {
                    "key": "${ip}",
                    "name": "目标IP",
                    "value": "10.0.0.1",
                    "custom_type": "input",
                    "source_type": "custom",
                    "show_type": "show",
                },
                "${hidden_var}": {
                    "key": "${hidden_var}",
                    "name": "隐藏变量",
                    "value": "secret",
                    "custom_type": "input",
                    "source_type": "custom",
                    "show_type": "hide",
                },
            }
        }
        mock_pipeline_instance.name = "测试任务"
        mock_pipeline_instance.executor = "admin"
        mock_pipeline_instance.create_time.strftime.return_value = "2026-03-20 10:30:00"

        mock_task = MagicMock()
        mock_task.id = 123
        mock_task.pipeline_instance = mock_pipeline_instance

        mock_filter.return_value.order_by.return_value.select_related.return_value.first.return_value = mock_task

        request = MockJsonBodyRequest("GET", {})
        request.GET = {"template_id": "1", "template_source": "project"}
        result = api.last_execution_constants(request, TEST_PROJECT_ID)

        self.assertTrue(result["result"])
        self.assertEqual(result["data"]["task_id"], 123)
        self.assertEqual(result["data"]["task_name"], "测试任务")
        self.assertEqual(result["data"]["executor"], "admin")
        self.assertIn("${ip}", result["data"]["constants"])
        self.assertNotIn("${hidden_var}", result["data"]["constants"])
        returned_ip = result["data"]["constants"]["${ip}"]
        self.assertEqual(returned_ip["value"], "10.0.0.1")
        self.assertEqual(returned_ip["name"], "目标IP")
        self.assertEqual(returned_ip["custom_type"], "input")

    @mock.patch("gcloud.taskflow3.apis.django.api.JsonResponse", MockJsonResponse())
    @mock.patch("gcloud.taskflow3.apis.django.api.TaskFlowInstance.objects.filter")
    def test_last_execution_constants__no_history(self, mock_filter):
        mock_filter.return_value.order_by.return_value.select_related.return_value.first.return_value = None

        request = MockJsonBodyRequest("GET", {})
        request.GET = {"template_id": "1", "template_source": "project"}
        result = api.last_execution_constants(request, TEST_PROJECT_ID)

        self.assertFalse(result["result"])
