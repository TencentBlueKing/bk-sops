# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""


from django.test import TestCase
from mock import MagicMock, patch

from pipeline_plugins.variables.collections.sites.open.cc import VarCmdbIpSelector


class VarCmdbIpSelectorTestCase(TestCase):
    def setUp(self):
        self.name = "name_token"
        self.value = {
            "selectors": ["ip"],
            "separator": ";",
            "topo": [],
            "ip": [
                {
                    "bk_host_name": "name1",
                    "bk_cloud_id": 0,
                    "bk_host_innerip": "1.1.1.1",
                    "bk_host_id": 1,
                    "cloud": [{"id": "0", "bk_inst_name": "default area"}],
                    "agent": 0,
                },
                {
                    "bk_host_name": "name2",
                    "bk_cloud_id": 0,
                    "bk_host_innerip": "2.2.2.2",
                    "bk_host_id": 2,
                    "cloud": [{"id": "0", "bk_inst_name": "default area"}],
                    "agent": 1,
                },
            ],
            "filters": [],
            "excludes": [],
            "with_cloud_id": True,
            "group": [{"id": "group1", "name": "group_test", "create_user": "tester"}],
        }
        self.context = {}
        self.pipeline_data = {"executor": "tester", "project_id": 1, "tenant_id": "test"}
        self.supplier_account = "supplier_account_token"
        ip_result = {
            "result": True,
            "code": 0,
            "data": [
                {
                    "bk_host_id": 1,
                    "bk_host_innerip": "1.1.1.1",
                    "bk_host_outerip": "",
                    "bk_host_name": "name1",
                    "bk_cloud_id": 0,
                },
                {
                    "bk_host_id": 2,
                    "bk_host_innerip": "2.2.2.2",
                    "bk_host_outerip": "",
                    "bk_host_name": "name2",
                    "bk_cloud_id": 0,
                },
            ],
        }
        mock_get_ip_picker_result = MagicMock(return_value=ip_result)
        mock_project_obj = MagicMock()
        mock_project_obj.from_cmdb = True
        mock_project_obj.bk_biz_id = 1
        mock_project = MagicMock()
        mock_project.objects.get = MagicMock(return_value=mock_project_obj)
        self.supplier_account_for_project_patcher = patch(
            "pipeline_plugins.variables.collections.sites.open.cc.supplier_account_for_project",
            MagicMock(return_value=self.supplier_account),
        )
        self.project_patcher = patch("pipeline_plugins.variables.collections.sites.open.cc.Project", mock_project,)
        self.get_ip_picker_result_patcher = patch(
            "pipeline_plugins.variables.collections.sites.open.cc.get_ip_picker_result", mock_get_ip_picker_result,
        )
        self.supplier_account_for_project_patcher.start()
        self.project_patcher.start()
        self.get_ip_picker_result_patcher.start()

    def tearDown(self):
        self.supplier_account_for_project_patcher.stop()
        self.project_patcher.stop()
        self.get_ip_picker_result_patcher.stop()

    def test_get_value_with_separator(self):
        ip_selector = VarCmdbIpSelector(self.name, self.value, self.context, self.pipeline_data)
        ip_data = ip_selector.get_value()
        self.assertEqual(ip_data, "0:1.1.1.1;0:2.2.2.2")

        self.value["separator"] = "|"
        ip_selector = VarCmdbIpSelector(self.name, self.value, self.context, self.pipeline_data)
        ip_data = ip_selector.get_value()
        self.assertEqual(ip_data, "0:1.1.1.1|0:2.2.2.2")

    def test_get_value_without_separator(self):
        self.value.pop("separator")
        ip_selector = VarCmdbIpSelector(self.name, self.value, self.context, self.pipeline_data)
        ip_data = ip_selector.get_value()
        self.assertEqual(ip_data, "0:1.1.1.1,0:2.2.2.2")
