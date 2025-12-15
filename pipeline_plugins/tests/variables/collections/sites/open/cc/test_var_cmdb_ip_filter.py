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
        client.api.ipchooser_host_details = MagicMock(return_value=get_agent_status_result)

        # Mock cc_get_host_by_innerip_with_ipv6 to return host information
        mock_host_result = {
            "result": True,
            "data": [
                {
                    "bk_host_id": 1,
                    "bk_host_innerip": "1.1.1.1",
                    "bk_host_innerip_v6": "",
                    "bk_cloud_id": 0,
                    "bk_agent_id": "0:1.1.1.1",
                },
                {
                    "bk_host_id": 2,
                    "bk_host_innerip": "2.2.2.2",
                    "bk_host_innerip_v6": "",
                    "bk_cloud_id": 0,
                    "bk_agent_id": "0:2.2.2.2",
                },
                {
                    "bk_host_id": 3,
                    "bk_host_innerip": "3.3.3.3",
                    "bk_host_innerip_v6": "",
                    "bk_cloud_id": 1,
                    "bk_agent_id": "1:3.3.3.3",
                },
                {
                    "bk_host_id": 4,
                    "bk_host_innerip": "4.4.4.4",
                    "bk_host_innerip_v6": "",
                    "bk_cloud_id": 2,
                    "bk_agent_id": "2:4.4.4.4",
                },
            ],
        }

        self.project_patcher = patch(
            "pipeline_plugins.variables.collections.sites.open.ip_filter_base.Project", mock_project
        )
        self.client = patch(
            "pipeline_plugins.variables.collections.sites.open.ip_filter_base.get_client_by_username",
            MagicMock(return_value=client),
        )
        self.cc_get_host_patcher = patch(
            "pipeline_plugins.variables.collections.sites.open.ip_filter_base.cc_get_host_by_innerip_with_ipv6",
            MagicMock(return_value=mock_host_result),
        )

        # Mock get_gse_agent_status_ipv6 to return agent status information
        mock_agent_status = {
            "0:1.1.1.1": 1,  # online
            "0:2.2.2.2": 0,  # offline
            "1:3.3.3.3": 1,  # online
            "2:4.4.4.4": 0,  # offline
        }
        self.gse_agent_status_patcher = patch(
            "pipeline_plugins.variables.collections.sites.open.ip_filter_base.get_gse_agent_status_ipv6",
            MagicMock(return_value=mock_agent_status),
        )

        self.project_patcher.start()
        self.client.start()
        self.cc_get_host_patcher.start()
        self.gse_agent_status_patcher.start()

    def tearDown(self):
        self.project_patcher.stop()
        self.client.stop()
        self.cc_get_host_patcher.stop()
        self.gse_agent_status_patcher.stop()

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
