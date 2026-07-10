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

from gcloud.core.models import Project
from gcloud.plugin_gateway.exceptions import PluginGatewayContextResolveError
from gcloud.plugin_gateway.models import PluginGatewaySourceConfig
from gcloud.plugin_gateway.services.context import PluginGatewayContextService


class PluginGatewayContextResolveTestCase(TestCase):
    def setUp(self):
        self.project = Project.objects.create(name="biz2", creator="admin", bk_biz_id=2, from_cmdb=True)
        self.source_config = PluginGatewaySourceConfig.objects.create(
            source_key="bkflow",
            display_name="BKFlow",
            default_project_id=None,
            scope_project_map={"space:88": self.project.id},
            plugin_allow_list=["plugin_job_execute"],
        )

    def test_biz_scope_resolves_project_and_operator(self):
        context = {"scope_type": "biz", "scope_value": "2", "operator": "zhangsan", "task_id": "task-001"}

        resolved = PluginGatewayContextService.resolve_run_context(self.source_config, context)

        self.assertEqual(resolved["project_id"], self.project.id)
        self.assertEqual(resolved["bk_biz_id"], 2)
        self.assertEqual(resolved["operator"], "zhangsan")
        self.assertEqual(resolved["scope_type"], "biz")
        self.assertEqual(resolved["scope_value"], "2")
        self.assertEqual(resolved["task_id"], "task-001")

    def test_mapping_table_resolves_non_biz_scope(self):
        context = {"scope_type": "space", "scope_value": "88", "operator": "lisi"}

        resolved = PluginGatewayContextService.resolve_run_context(self.source_config, context)

        self.assertEqual(resolved["project_id"], self.project.id)
        self.assertEqual(resolved["bk_biz_id"], 2)
        self.assertEqual(resolved["operator"], "lisi")

    def test_default_project_fallback(self):
        self.source_config.default_project_id = self.project.id
        self.source_config.scope_project_map = {}
        self.source_config.save()

        resolved = PluginGatewayContextService.resolve_run_context(self.source_config, None)

        self.assertEqual(resolved["project_id"], self.project.id)
        self.assertEqual(resolved["bk_biz_id"], 2)
        self.assertEqual(resolved["operator"], "")

    def test_unresolved_context_raises(self):
        self.source_config.scope_project_map = {}
        self.source_config.default_project_id = None
        self.source_config.save()

        with self.assertRaises(PluginGatewayContextResolveError):
            PluginGatewayContextService.resolve_run_context(
                self.source_config,
                {"scope_type": "other", "scope_value": "x"},
            )

    def test_missing_mapped_project_raises(self):
        self.source_config.scope_project_map = {"space:404": 404}
        self.source_config.save()

        with self.assertRaises(PluginGatewayContextResolveError):
            PluginGatewayContextService.resolve_run_context(
                self.source_config,
                {"scope_type": "space", "scope_value": "404"},
            )
