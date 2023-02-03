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

from gcloud.taskflow3.models import AutoRetryNodeStrategy
from gcloud.taskflow3.utils import parse_node_timeout_configs, extract_failed_nodes, get_failed_nodes_info


class UtilsTestCase(TestCase):
    def setUp(self):
        self.arn_instance = AutoRetryNodeStrategy.objects.create(
            taskflow_id=1, root_pipeline_id="root_pipeline_id", node_id="act_1", max_retry_times=5
        )
        self.arn_instance.save()

    def tearDown(self):
        self.arn_instance.delete()

    def test_parse_node_timeout_configs_success(self):
        pipeline_tree = {
            "activities": {
                "act_1": {
                    "type": "ServiceActivity",
                    "timeout_config": {"enable": True, "seconds": 2, "action": "forced_fail"},
                },
                "act_2": {
                    "type": "ServiceActivity",
                    "timeout_config": {"enable": True, "seconds": 2, "action": "forced_fail_and_skip"},
                },
            }
        }
        parse_configs = [
            {"action": "forced_fail", "node_id": "act_1", "timeout": 2},
            {"action": "forced_fail_and_skip", "node_id": "act_2", "timeout": 2},
        ]
        parse_result = parse_node_timeout_configs(pipeline_tree)
        self.assertEqual(parse_result["result"], True)
        self.assertEqual(parse_result["data"], parse_configs)

    def test_parse_node_timeout_configs_fail_and_ignore(self):
        pipeline_tree = {
            "activities": {
                "act_1": {
                    "type": "ServiceActivity",
                    "timeout_config": {"enable": True, "seconds": "test_fail", "action": "forced_fail"},
                },
                "act_2": {
                    "type": "ServiceActivity",
                    "timeout_config": {"enable": True, "seconds": 2, "action": "forced_fail_and_skip"},
                },
            }
        }
        parse_configs = [
            {"action": "forced_fail_and_skip", "node_id": "act_2", "timeout": 2},
        ]
        parse_result = parse_node_timeout_configs(pipeline_tree)
        self.assertEqual(parse_result["result"], True)
        self.assertEqual(parse_result["data"], parse_configs)

    def test_extract_failed_nodes(self):
        status_tree = {
            "id": "root_pipeline_id",
            "children": {
                "act_1": {"id": "act_1", "state": "FINISHED", "children": {}},
                "act_2": {
                    "id": "act_2",
                    "state": "FAILED",
                    "children": {
                        "act_2_1": {"id": "act_2_1", "state": "FINISHED", "children": {}},
                        "act_2_2": {"id": "act_2_2", "state": "FAILED", "children": {}},
                    },
                },
                "act_3": {"id": "act_3", "state": "FINISHED", "children": {}},
            },
            "state": "FAILED",
        }
        failed_nodes = extract_failed_nodes(status_tree)
        self.assertEqual(failed_nodes, ["act_2", "act_2_2"])

    def test_get_failed_nodes_info(self):
        FAILED_NODES_INFO = {
            "act_1": {
                "auto_retry_times": self.arn_instance.retry_times,
                "max_auto_retry_times": self.arn_instance.max_retry_times,
            },
            "act_2": {},
        }
        failed_nodes_info = get_failed_nodes_info("root_pipeline_id", ["act_1", "act_2"])
        self.assertEqual(failed_nodes_info, FAILED_NODES_INFO)
