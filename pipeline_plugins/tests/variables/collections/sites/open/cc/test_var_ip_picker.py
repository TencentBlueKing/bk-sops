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
from mock import MagicMock, patch

from pipeline_plugins.variables.collections.sites.open.cc import VarIpPickerVariable


class VarIpPickerVariableTestCase(TestCase):
    def setUp(self):
        self.pipeline_data = {
            "executor": "admin",
            "project_id": 1,
            "tenant_id": "tenant",
        }
        self.context = {}

        # Mock Project
        self.project_patcher = patch("pipeline_plugins.variables.collections.sites.open.cc.Project")
        self.mock_project_cls = self.project_patcher.start()
        self.mock_project = MagicMock()
        self.mock_project.from_cmdb = True
        self.mock_project.bk_biz_id = 1
        self.mock_project_cls.objects.get.return_value = self.mock_project

    def tearDown(self):
        self.project_patcher.stop()

    @patch("pipeline_plugins.variables.collections.sites.open.cc.cc_get_ips_info_by_str")
    def test_get_value_custom(self, mock_get_ips):
        value = {
            "var_ip_method": "custom",
            "var_ip_custom_value": "1.1.1.1",
        }
        mock_get_ips.return_value = {"ip_result": [{"InnerIP": "1.1.1.1"}]}

        var = VarIpPickerVariable("name", value, self.context, self.pipeline_data)
        result = var.get_value()
        self.assertEqual(result, "1.1.1.1")

    @patch("pipeline_plugins.variables.collections.sites.open.cc.cc_get_inner_ip_by_module_id")
    @patch("pipeline_plugins.variables.collections.sites.open.cc.cc_get_ips_info_by_str")
    def test_get_value_tree(self, mock_get_ips, mock_get_by_module):
        value = {
            "var_ip_method": "tree",
            "var_ip_tree": ["ip_1.1.1.1", "module_10"],
        }
        # Mock tree IP part
        mock_get_ips.return_value = {"ip_result": [{"InnerIP": "1.1.1.1"}]}

        # Mock module part
        mock_get_by_module.return_value = [{"host": {"bk_host_innerip": "2.2.2.2"}}]

        var = VarIpPickerVariable("name", value, self.context, self.pipeline_data)
        result = var.get_value()
        self.assertTrue("1.1.1.1" in result)
        self.assertTrue("2.2.2.2" in result)

    def test_get_value_missing_params(self):
        var = VarIpPickerVariable("name", {}, {}, {})
        with self.assertRaises(Exception):
            var.get_value()
