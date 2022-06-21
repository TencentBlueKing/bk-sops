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

from gcloud.taskflow3.utils import parse_node_timeout_configs


class UtilsTestCase(TestCase):
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
