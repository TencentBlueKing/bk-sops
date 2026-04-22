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
