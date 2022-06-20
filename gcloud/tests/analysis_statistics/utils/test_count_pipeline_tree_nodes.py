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

from pipeline.utils.uniqid import node_uniqid

from gcloud.analysis_statistics.utils import count_pipeline_tree_nodes

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


class TestCountPipelineTreeNodes(TestCase):
    def test_count_pipeline_tree_nodes(self):
        assert_data = (2, 0, 0)
        atom_total, subprocess_total, gateways_total = count_pipeline_tree_nodes(TEST_PIPELINE_TREE)
        data = (atom_total, subprocess_total, gateways_total)
        self.assertEqual(data, assert_data)
