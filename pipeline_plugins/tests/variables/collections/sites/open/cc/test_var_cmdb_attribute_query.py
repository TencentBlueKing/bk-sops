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

from mock import MagicMock, patch

from django.test import TestCase

from pipeline_plugins.variables.collections.sites.open.cc import VarCmdbAttributeQuery


class VarCmdbAttributeQueryTestCase(TestCase):
    def setUp(self):
        self.name = "name_token"
        self.value = "  1.1.1.1 \n2.2.2.2 3.3.3.3\n4.4.4.4"
        self.context = {}
        self.executer = "tester"
        self.pipeline_data = {
            "executor": self.executer,
            "project_id": 1,
        }
        self.bk_biz_id = "bk_biz_id_token"
        self.supplier_account = "supplier_account_token"
        self.get_business_host_return = [
            {"bk_host_innerip": "1.1.1.1", "bk_cloud_id": 1, "bk_attr": 1},
            {"bk_host_innerip": "1.1.1.2", "bk_cloud_id": 2, "bk_attr": 2},
            {"bk_host_innerip": "1.1.1.3", "bk_attr": 3},
        ]

        mock_project_obj = MagicMock()
        mock_project_obj.bk_biz_id = self.bk_biz_id
        mock_project = MagicMock()
        mock_project.objects.get = MagicMock(return_value=mock_project_obj)
        self.project_patcher = patch("pipeline_plugins.variables.collections.sites.open.cc.Project", mock_project)
        self.supplier_account_for_project_patcher = patch(
            "pipeline_plugins.variables.collections.sites.open.cc.supplier_account_for_project",
            MagicMock(return_value=self.supplier_account),
        )

        self.project_patcher.start()
        self.supplier_account_for_project_patcher.start()

    def tearDown(self):
        self.project_patcher.stop()
        self.supplier_account_for_project_patcher.stop()

    def test_get_value(self):
        mock_get_business_host = MagicMock(return_value=self.get_business_host_return)
        host_attrs_query = VarCmdbAttributeQuery(self.name, self.value, self.context, self.pipeline_data)
        with patch("pipeline_plugins.variables.collections.sites.open.cc.get_business_host", mock_get_business_host):
            value = host_attrs_query.get_value()

        self.assertEqual(
            value,
            {
                "1.1.1.1": {"bk_host_innerip": "1.1.1.1", "bk_attr": 1},
                "1.1.1.2": {"bk_host_innerip": "1.1.1.2", "bk_attr": 2},
                "1.1.1.3": {"bk_host_innerip": "1.1.1.3", "bk_attr": 3},
            },
        )
        mock_get_business_host.assert_called_once_with(
            self.executer,
            self.bk_biz_id,
            self.supplier_account,
            [
                "bk_cpu",
                "bk_isp_name",
                "bk_os_name",
                "bk_province_name",
                "bk_host_id",
                "import_from",
                "bk_os_version",
                "bk_disk",
                "operator",
                "bk_mem",
                "bk_host_name",
                "bk_host_innerip",
                "bk_comment",
                "bk_os_bit",
                "bk_outer_mac",
                "bk_asset_id",
                "bk_service_term",
                "bk_sla",
                "bk_cpu_mhz",
                "bk_host_outerip",
                "bk_state_name",
                "bk_os_type",
                "bk_mac",
                "bk_bak_operator",
                "bk_supplier_account",
                "bk_sn",
                "bk_cpu_module",
            ],
            ["1.1.1.1", "2.2.2.2", "3.3.3.3", "4.4.4.4"],
        )
