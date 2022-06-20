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
from mock import MagicMock, patch
from django.test import TestCase

from gcloud.taskflow3.models import TimeoutNodeConfig


class BatchCreateNodeTimeoutConfigTestCase(TestCase):
    def setUp(self):
        self.taskflow_id = 1
        self.pipeline_tree = {}
        self.root_pipeline_id = "root_pipeline_id"
        self.parsed_configs = [
            {"action": "forced_fail", "node_id": "act_1", "timeout": 2},
            {"action": "forced_fail_and_skip", "node_id": "act_2", "timeout": 2},
        ]

    def test_batch_create_node_time_config_success(self):
        config_parse_result = {"result": True, "data": self.parsed_configs, "message": ""}
        with patch("gcloud.taskflow3.models.parse_node_timeout_configs", MagicMock(return_value=config_parse_result)):
            TimeoutNodeConfig.objects.batch_create_node_timeout_config(
                self.taskflow_id, self.root_pipeline_id, self.pipeline_tree
            )
            config_count = len(TimeoutNodeConfig.objects.all())
            self.assertEqual(config_count, 2)

    def test_batch_create_node_time_config_fail(self):
        config_parse_result = {"result": False, "data": "", "message": "test fail"}
        with patch("gcloud.taskflow3.models.parse_node_timeout_configs", MagicMock(return_value=config_parse_result)):
            TimeoutNodeConfig.objects.batch_create_node_timeout_config(
                self.taskflow_id, self.root_pipeline_id, self.pipeline_tree
            )
            config_count = TimeoutNodeConfig.objects.count()
            self.assertEqual(config_count, 0)
