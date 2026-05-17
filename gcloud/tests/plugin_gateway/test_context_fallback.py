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

from gcloud.plugin_gateway.models import PluginGatewaySourceConfig
from gcloud.plugin_gateway.services.context import PluginGatewayContextService


class PluginGatewayContextFallbackTestCase(TestCase):
    def test_build_trigger_payload_uses_default_project(self):
        source_config = PluginGatewaySourceConfig.objects.create(
            source_key="bkflow",
            display_name="BKFlow",
            default_project_id=2001,
            callback_domain_allow_list=["bkflow.example.com"],
            plugin_allow_list=["plugin_job_execute"],
            is_enabled=True,
        )

        payload = PluginGatewayContextService.build_trigger_payload(
            source_config=source_config,
            plugin_id="plugin_job_execute",
            payload={"inputs": {"biz_id": 2}},
        )

        self.assertEqual(payload["project_id"], 2001)

    def test_build_trigger_payload_rejects_plugin_outside_allow_list(self):
        source_config = PluginGatewaySourceConfig.objects.create(
            source_key="bkflow",
            display_name="BKFlow",
            default_project_id=2001,
            callback_domain_allow_list=["bkflow.example.com"],
            plugin_allow_list=["plugin_job_execute"],
            is_enabled=True,
        )

        with self.assertRaises(ValueError):
            PluginGatewayContextService.build_trigger_payload(
                source_config=source_config,
                plugin_id="plugin_job_status",
                payload={"inputs": {"biz_id": 2}},
            )

    def test_validate_callback_domain_rejects_empty_allow_list(self):
        source_config = PluginGatewaySourceConfig.objects.create(
            source_key="bkflow",
            display_name="BKFlow",
            callback_domain_allow_list=[],
            plugin_allow_list=["plugin_job_execute"],
            is_enabled=True,
        )

        with self.assertRaises(ValueError):
            PluginGatewayContextService.validate_callback_domain(
                source_config=source_config,
                callback_url="https://bkflow.example.com/callback",
            )
