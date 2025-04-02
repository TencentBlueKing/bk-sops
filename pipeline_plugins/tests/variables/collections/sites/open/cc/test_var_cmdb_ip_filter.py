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

from pipeline_plugins.variables.collections.sites.open.cc import VarCmdbIpFilter


class VarCmdbIpSelectorTestCase(TestCase):
    def setUp(self):
        self.tenant_id = "test"
        self.name = "name_token"
        self.value = {
            "origin_ips": "1.1.1.1\n2.2.2.2\n1:3.3.3.3\n2:4.4.4.4",
            "gse_agent_status": 1,
        }
        self.context = {}
        self.pipeline_data = {"executor": "tester", "project_id": 1, "tenant_id": self.tenant_id}
        self.supplier_account = "supplier_account_token"
        get_agent_status_result = {
            "result": True,
            "code": 0,
            "data": [
                {"ip": "1.1.1.1", "alive": 1, "cloud_area": {"id": 0, "ip": "1.1.1.1"}},
                {"ip": "2.2.2.2", "alive": 0, "cloud_area": {"id": 0, "ip": "2.2.2.2"}},
                {"ip": "3.3.3.3", "alive": 1, "cloud_area": {"id": 1, "ip": "3.3.3.3"}},
                {"ip": "4.4.4.4", "alive": 0, "cloud_area": {"id": 2, "ip": "3.3.3.3"}},
            ],
        }
        mock_project_obj = MagicMock()
        mock_project_obj.from_cmdb = True
        mock_project_obj.bk_biz_id = 1
        mock_project = MagicMock()
        mock_project.objects.get = MagicMock(return_value=mock_project_obj)

        client = MagicMock()
        client.get_ipchooser_host_details = MagicMock(return_value=get_agent_status_result)

        self.supplier_account_for_project_patcher = patch(
            "pipeline_plugins.variables.collections.sites.open.ip_filter_base.supplier_id_for_project",
            MagicMock(return_value=self.supplier_account),
        )
        self.project_patcher = patch(
            "pipeline_plugins.variables.collections.sites.open.ip_filter_base.Project", mock_project
        )
        self.client = patch(
            "pipeline_plugins.variables.collections.sites.open.ip_filter_base.get_nodeman_client_by_username",
            MagicMock(return_value=client),
        )

        self.supplier_account_for_project_patcher.start()
        self.project_patcher.start()
        self.client.start()

    def tearDown(self):
        self.supplier_account_for_project_patcher.stop()
        self.project_patcher.stop()
        self.client.stop()

    def test_get_value_with_gse_agent_online(self):
        ip_filters = VarCmdbIpFilter(self.name, self.value, self.context, self.pipeline_data)
        match_ip = ip_filters.get_value()
        self.assertEqual(match_ip, "0:1.1.1.1,1:3.3.3.3")

    def test_get_value_gse_agent_offline(self):
        self.value = {
            "origin_ips": "1.1.1.1,2.2.2.2,1:3.3.3.3,2:4.4.4.4",
            "gse_agent_status": 0,
        }
        ip_filters = VarCmdbIpFilter(self.name, self.value, self.context, self.pipeline_data)
        match_ip = ip_filters.get_value()
        self.assertEqual(match_ip, "0:2.2.2.2,2:4.4.4.4")
