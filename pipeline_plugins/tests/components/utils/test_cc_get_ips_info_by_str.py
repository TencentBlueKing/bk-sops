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

from pipeline_plugins.components.utils.sites.open.utils import cc_get_ips_info_by_str


class CCGetIPsInfoByStrTestCase(TestCase):
    def setUp(self):
        self.username = "tester"
        self.biz_cc_id = 123
        self.supplier_account = "test_supplier_account"
        self.maxDiff = None
        self.tenant_id = "system"

    def test_ip_format(self):
        ip_str = "1.1.1.1,2.2.2.2\n3.3.3.3,4.4.4.4"
        get_business_host_topo_return = [
            {
                "host": {"bk_host_id": 1, "bk_host_innerip": "1.1.1.1", "bk_cloud_id": 0},
                "module": [{"bk_module_id": 1, "bk_module_name": "module_1"}],
                "set": [{"bk_set_id": 1, "bk_set_name": "set_1"}],
            },
            {
                "host": {"bk_host_id": 2, "bk_host_innerip": "2.2.2.2", "bk_cloud_id": 0},
                "module": [{"bk_module_id": 2, "bk_module_name": "module_2"}],
                "set": [{"bk_set_id": 2, "bk_set_name": "set_2"}],
            },
            {
                "host": {"bk_host_id": 3, "bk_host_innerip": "3.3.3.3", "bk_cloud_id": 0},
                "module": [{"bk_module_id": 3, "bk_module_name": "module_3"}],
                "set": [{"bk_set_id": 3, "bk_set_name": "set_3"}],
            },
        ]
        cmdb = MagicMock()
        cmdb.get_business_host_topo = MagicMock(return_value=get_business_host_topo_return)

        with patch("pipeline_plugins.components.utils.sites.open.utils.cmdb", cmdb):
            result = cc_get_ips_info_by_str(
                tenant_id=self.tenant_id, username=self.username, biz_cc_id=self.biz_cc_id, ip_str=ip_str
            )

        cmdb.get_business_host_topo.assert_called_once_with(
            tenant_id=self.tenant_id,
            username=self.username,
            bk_biz_id=self.biz_cc_id,
            host_fields=["bk_host_innerip", "bk_host_id", "bk_cloud_id"],
            ip_list=["1.1.1.1", "2.2.2.2", "3.3.3.3", "4.4.4.4"],
        )
        self.assertEqual(result["result"], True)
        self.assertEqual(
            result["ip_result"],
            [
                {
                    "InnerIP": "1.1.1.1",
                    "HostID": 1,
                    "Source": 0,
                    "Sets": [{"bk_set_id": 1, "bk_set_name": "set_1"}],
                    "Modules": [{"bk_module_id": 1, "bk_module_name": "module_1"}],
                },
                {
                    "InnerIP": "2.2.2.2",
                    "HostID": 2,
                    "Source": 0,
                    "Sets": [{"bk_set_id": 2, "bk_set_name": "set_2"}],
                    "Modules": [{"bk_module_id": 2, "bk_module_name": "module_2"}],
                },
                {
                    "InnerIP": "3.3.3.3",
                    "HostID": 3,
                    "Source": 0,
                    "Sets": [{"bk_set_id": 3, "bk_set_name": "set_3"}],
                    "Modules": [{"bk_module_id": 3, "bk_module_name": "module_3"}],
                },
            ],
        )
        self.assertEqual(result["ip_count"], 3)
        self.assertEqual(result["invalid_ip"], ["4.4.4.4"])

    def test_ip_format_with_multi_innerip(self):
        ip_str = "1.1.1.1,2.2.2.2\n3.3.3.3,4.4.4.4"
        get_business_host_topo_return = [
            {
                "host": {"bk_host_id": 1, "bk_host_innerip": "1.2.3.4,1.1.1.1", "bk_cloud_id": 0},
                "module": [{"bk_module_id": 1, "bk_module_name": "module_1"}],
                "set": [{"bk_set_id": 1, "bk_set_name": "set_1"}],
            },
            {
                "host": {"bk_host_id": 2, "bk_host_innerip": "", "bk_cloud_id": 0},
                "module": [{"bk_module_id": 2, "bk_module_name": "module_2"}],
                "set": [{"bk_set_id": 2, "bk_set_name": "set_2"}],
            },
            {
                "host": {"bk_host_id": 3, "bk_host_innerip": "3.3.3.3", "bk_cloud_id": 0},
                "module": [{"bk_module_id": 3, "bk_module_name": "module_3"}],
                "set": [{"bk_set_id": 3, "bk_set_name": "set_3"}],
            },
        ]
        cmdb = MagicMock()
        cmdb.get_business_host_topo = MagicMock(return_value=get_business_host_topo_return)

        with patch("pipeline_plugins.components.utils.sites.open.utils.cmdb", cmdb):
            result = cc_get_ips_info_by_str(
                tenant_id=self.tenant_id, username=self.username, biz_cc_id=self.biz_cc_id, ip_str=ip_str
            )

        cmdb.get_business_host_topo.assert_called_once_with(
            tenant_id=self.tenant_id,
            username=self.username,
            bk_biz_id=self.biz_cc_id,
            host_fields=["bk_host_innerip", "bk_host_id", "bk_cloud_id"],
            ip_list=["1.1.1.1", "2.2.2.2", "3.3.3.3", "4.4.4.4"],
        )
        self.assertEqual(result["result"], True)
        self.assertEqual(
            result["ip_result"],
            [
                {
                    "InnerIP": "1.1.1.1",
                    "HostID": 1,
                    "Source": 0,
                    "Sets": [{"bk_set_id": 1, "bk_set_name": "set_1"}],
                    "Modules": [{"bk_module_id": 1, "bk_module_name": "module_1"}],
                },
                {
                    "InnerIP": "3.3.3.3",
                    "HostID": 3,
                    "Source": 0,
                    "Sets": [{"bk_set_id": 3, "bk_set_name": "set_3"}],
                    "Modules": [{"bk_module_id": 3, "bk_module_name": "module_3"}],
                },
            ],
        )
        self.assertEqual(result["ip_count"], 2)
        self.assertEqual(set(result["invalid_ip"]), {"2.2.2.2", "4.4.4.4"})

    def test_set_module_format(self):
        ip_str = "set_1|module_1|1.1.1.1,set_2|module_2|2.2.2.2\nset_3|module_3|3.3.3.3,set_3|module_3|4.4.4.4"
        get_business_host_topo_return = [
            {
                "host": {"bk_host_id": 1, "bk_host_innerip": "1.1.1.1", "bk_cloud_id": 0},
                "module": [{"bk_module_id": 1, "bk_module_name": "module_1"}],
                "set": [{"bk_set_id": 1, "bk_set_name": "set_1"}],
            },
            {
                "host": {"bk_host_id": 2, "bk_host_innerip": "2.2.2.2", "bk_cloud_id": 0},
                "module": [{"bk_module_id": 2, "bk_module_name": "module_2"}],
                "set": [{"bk_set_id": 2, "bk_set_name": "set_2"}],
            },
            {
                "host": {"bk_host_id": 3, "bk_host_innerip": "3.3.3.3", "bk_cloud_id": 0},
                "module": [{"bk_module_id": 3, "bk_module_name": "module_3"}],
                "set": [{"bk_set_id": 3, "bk_set_name": "set_3"}],
            },
        ]
        cmdb = MagicMock()
        cmdb.get_business_host_topo = MagicMock(return_value=get_business_host_topo_return)

        with patch("pipeline_plugins.components.utils.sites.open.utils.cmdb", cmdb):
            result = cc_get_ips_info_by_str(
                tenant_id=self.tenant_id, username=self.username, biz_cc_id=self.biz_cc_id, ip_str=ip_str
            )

        cmdb.get_business_host_topo.assert_called_once_with(
            tenant_id=self.tenant_id,
            username=self.username,
            bk_biz_id=self.biz_cc_id,
            host_fields=["bk_host_innerip", "bk_host_id", "bk_cloud_id"],
            ip_list=["1.1.1.1", "2.2.2.2", "3.3.3.3", "4.4.4.4"],
        )
        self.assertEqual(result["result"], True)
        self.assertEqual(
            result["ip_result"],
            [
                {
                    "InnerIP": "1.1.1.1",
                    "HostID": 1,
                    "Source": 0,
                    "Sets": [{"bk_set_id": 1, "bk_set_name": "set_1"}],
                    "Modules": [{"bk_module_id": 1, "bk_module_name": "module_1"}],
                    "SetID": 1,
                    "SetName": "set_1",
                    "ModuleID": 1,
                    "ModuleName": "module_1",
                },
                {
                    "InnerIP": "2.2.2.2",
                    "HostID": 2,
                    "Source": 0,
                    "Sets": [{"bk_set_id": 2, "bk_set_name": "set_2"}],
                    "Modules": [{"bk_module_id": 2, "bk_module_name": "module_2"}],
                    "SetID": 2,
                    "SetName": "set_2",
                    "ModuleID": 2,
                    "ModuleName": "module_2",
                },
                {
                    "InnerIP": "3.3.3.3",
                    "HostID": 3,
                    "Source": 0,
                    "Sets": [{"bk_set_id": 3, "bk_set_name": "set_3"}],
                    "Modules": [{"bk_module_id": 3, "bk_module_name": "module_3"}],
                    "SetID": 3,
                    "SetName": "set_3",
                    "ModuleID": 3,
                    "ModuleName": "module_3",
                },
            ],
        )
        self.assertEqual(result["ip_count"], 3)
        self.assertEqual(result["invalid_ip"], ["4.4.4.4"])

    def test_cloud_ip_format(self):
        ip_str = "0:1.1.1.1,0:2.2.2.2\n0:3.3.3.3,0:4.4.4.4"
        get_business_host_topo_return = [
            {
                "host": {"bk_host_id": 1, "bk_host_innerip": "1.1.1.1", "bk_cloud_id": 0},
                "module": [{"bk_module_id": 1, "bk_module_name": "module_1"}],
                "set": [{"bk_set_id": 1, "bk_set_name": "set_1"}],
            },
            {
                "host": {"bk_host_id": 2, "bk_host_innerip": "2.2.2.2", "bk_cloud_id": 0},
                "module": [{"bk_module_id": 2, "bk_module_name": "module_2"}],
                "set": [{"bk_set_id": 2, "bk_set_name": "set_2"}],
            },
            {
                "host": {"bk_host_id": 3, "bk_host_innerip": "3.3.3.3", "bk_cloud_id": 0},
                "module": [{"bk_module_id": 3, "bk_module_name": "module_3"}],
                "set": [{"bk_set_id": 3, "bk_set_name": "set_3"}],
            },
        ]
        cmdb = MagicMock()
        cmdb.get_business_host_topo = MagicMock(return_value=get_business_host_topo_return)

        with patch("pipeline_plugins.components.utils.sites.open.utils.cmdb", cmdb):
            result = cc_get_ips_info_by_str(
                tenant_id=self.tenant_id, username=self.username, biz_cc_id=self.biz_cc_id, ip_str=ip_str
            )

        cmdb.get_business_host_topo.assert_called_once_with(
            tenant_id=self.tenant_id,
            username=self.username,
            bk_biz_id=self.biz_cc_id,
            host_fields=["bk_host_innerip", "bk_host_id", "bk_cloud_id"],
            ip_list=["1.1.1.1", "2.2.2.2", "3.3.3.3", "4.4.4.4"],
        )
        self.assertEqual(result["result"], True)
        self.assertEqual(
            result["ip_result"],
            [
                {
                    "InnerIP": "1.1.1.1",
                    "HostID": 1,
                    "Source": 0,
                    "Sets": [{"bk_set_id": 1, "bk_set_name": "set_1"}],
                    "Modules": [{"bk_module_id": 1, "bk_module_name": "module_1"}],
                },
                {
                    "InnerIP": "2.2.2.2",
                    "HostID": 2,
                    "Source": 0,
                    "Sets": [{"bk_set_id": 2, "bk_set_name": "set_2"}],
                    "Modules": [{"bk_module_id": 2, "bk_module_name": "module_2"}],
                },
                {
                    "InnerIP": "3.3.3.3",
                    "HostID": 3,
                    "Source": 0,
                    "Sets": [{"bk_set_id": 3, "bk_set_name": "set_3"}],
                    "Modules": [{"bk_module_id": 3, "bk_module_name": "module_3"}],
                },
            ],
        )
        self.assertEqual(result["ip_count"], 3)
        self.assertEqual(result["invalid_ip"], ["4.4.4.4"])

    def test_cloud_ip_format_with_multi_innerip(self):
        ip_str = "0:1.1.1.1,0:2.2.2.2\n0:3.3.3.3,0:4.4.4.4"
        get_business_host_topo_return = [
            {
                "host": {"bk_host_id": 1, "bk_host_innerip": "1.2.3.4,1.1.1.1", "bk_cloud_id": 0},
                "module": [{"bk_module_id": 1, "bk_module_name": "module_1"}],
                "set": [{"bk_set_id": 1, "bk_set_name": "set_1"}],
            },
            {
                "host": {"bk_host_id": 2, "bk_host_innerip": "", "bk_cloud_id": 0},
                "module": [{"bk_module_id": 2, "bk_module_name": "module_2"}],
                "set": [{"bk_set_id": 2, "bk_set_name": "set_2"}],
            },
            {
                "host": {"bk_host_id": 3, "bk_host_innerip": "3.3.3.3", "bk_cloud_id": 0},
                "module": [{"bk_module_id": 3, "bk_module_name": "module_3"}],
                "set": [{"bk_set_id": 3, "bk_set_name": "set_3"}],
            },
        ]
        cmdb = MagicMock()
        cmdb.get_business_host_topo = MagicMock(return_value=get_business_host_topo_return)

        with patch("pipeline_plugins.components.utils.sites.open.utils.cmdb", cmdb):
            result = cc_get_ips_info_by_str(
                tenant_id=self.tenant_id, username=self.username, biz_cc_id=self.biz_cc_id, ip_str=ip_str
            )

        cmdb.get_business_host_topo.assert_called_once_with(
            tenant_id=self.tenant_id,
            username=self.username,
            bk_biz_id=self.biz_cc_id,
            host_fields=["bk_host_innerip", "bk_host_id", "bk_cloud_id"],
            ip_list=["1.1.1.1", "2.2.2.2", "3.3.3.3", "4.4.4.4"],
        )
        self.assertEqual(result["result"], True)
        self.assertEqual(
            result["ip_result"],
            [
                {
                    "InnerIP": "1.1.1.1",
                    "HostID": 1,
                    "Source": 0,
                    "Sets": [{"bk_set_id": 1, "bk_set_name": "set_1"}],
                    "Modules": [{"bk_module_id": 1, "bk_module_name": "module_1"}],
                },
                {
                    "InnerIP": "3.3.3.3",
                    "HostID": 3,
                    "Source": 0,
                    "Sets": [{"bk_set_id": 3, "bk_set_name": "set_3"}],
                    "Modules": [{"bk_module_id": 3, "bk_module_name": "module_3"}],
                },
            ],
        )
        self.assertEqual(result["ip_count"], 2)
        self.assertEqual(set(result["invalid_ip"]), {"2.2.2.2", "4.4.4.4"})
