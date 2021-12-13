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

from gcloud.taskflow3.models import TimeoutNodeConfig


class BatchCreateNodeTimeoutConfigTestCase(TestCase):
    def setUp(self):
        self.taskflow_id = 1
        self.pipeline_tree = {
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
        self.root_pipeline_id = "root_pipeline_id"

    def test_batch_create_node_time_config_success(self):
        TimeoutNodeConfig.objects.batch_create_node_timeout_config(
            self.taskflow_id, self.root_pipeline_id, self.pipeline_tree
        )
        config_count = len(TimeoutNodeConfig.objects.all())
        self.assertEqual(config_count, 2)

    def test_batch_create_node_time_config_fail(self):
        self.pipeline_tree["activities"]["act_1"]["timeout_config"].pop("seconds")
        TimeoutNodeConfig.objects.batch_create_node_timeout_config(
            self.taskflow_id, self.root_pipeline_id, self.pipeline_tree
        )
        config_count = len(TimeoutNodeConfig.objects.all())
        self.assertEqual(config_count, 1)
