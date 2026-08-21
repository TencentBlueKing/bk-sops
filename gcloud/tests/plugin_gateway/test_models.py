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

from gcloud.plugin_gateway.models import PluginGatewayRun, PluginGatewaySourceConfig


class PluginGatewayModelsTestCase(TestCase):
    def test_model_verbose_name_aliases(self):
        self.assertEqual(PluginGatewaySourceConfig._meta.verbose_name, "插件网关来源配置")
        self.assertEqual(PluginGatewaySourceConfig._meta.verbose_name_plural, "插件网关来源配置")
        self.assertEqual(PluginGatewayRun._meta.verbose_name, "插件网关执行记录")
        self.assertEqual(PluginGatewayRun._meta.verbose_name_plural, "插件网关执行记录")

    def test_run_has_idempotent_constraint_per_app(self):
        constraint_names = {constraint.name for constraint in PluginGatewayRun._meta.constraints}

        self.assertIn("uniq_plugin_gateway_app_request", constraint_names)

    def test_source_config_full_capability_fields(self):
        cfg = PluginGatewaySourceConfig.objects.create(
            source_key="sops",
            display_name="标准运维",
            callback_domain_allow_list=["bkflow.example.com"],
            scope_project_map={"biz:2": 10},
            do_not_open_list=["builtin__pause_node"],
            execution_timeout_seconds=7200,
        )

        self.assertEqual(cfg.scope_project_map["biz:2"], 10)
        self.assertEqual(cfg.do_not_open_list, ["builtin__pause_node"])
        self.assertEqual(cfg.execution_timeout_seconds, 7200)

    def test_source_config_does_not_have_plugin_allow_list(self):
        field_names = {field.name for field in PluginGatewaySourceConfig._meta.fields}

        self.assertNotIn("plugin_allow_list", field_names)

    def test_run_has_running_state_and_runtime_fields(self):
        self.assertEqual(PluginGatewayRun.Status.CREATED, "CREATED")
        self.assertEqual(PluginGatewayRun.Status.RUNNING, "RUNNING")
        self.assertNotIn(PluginGatewayRun.Status.RUNNING, PluginGatewayRun.Status.TERMINAL)

        run = PluginGatewayRun.objects.create(
            source_key="sops",
            plugin_id="builtin__job_execute_task",
            plugin_version="legacy",
            client_request_id="req-1",
            open_plugin_run_id="a" * 32,
            callback_url="https://bkflow.example.com/cb",
            callback_token="tok",
            run_status=PluginGatewayRun.Status.CREATED,
            caller_app_code="bkflow",
        )

        self.assertEqual(run.runtime_outputs, {})
        self.assertEqual(run.schedule_times, 0)
        self.assertIsNone(run.execution_expire_at)
