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

import mock
from django.test import TestCase

from pipeline_plugins.components.utils.sites.open.utils import (
    cc_get_ips_info_by_str,
    cc_get_ips_info_by_str_ipv6,
    compare_ip_list_and_return,
    get_biz_ip_from_frontend,
    get_biz_ip_from_frontend_hybrid,
    get_difference_ip_list,
    get_host_info_list,
    get_ipv4_info_list,
    get_ipv4_info_list_with_cloud_id,
    get_ipv6_info_list,
    get_ipv6_info_list_with_cloud_id,
    get_module_id_list_by_name,
    get_nodeman_job_url,
    get_repeat_ip,
)


class UtilsV2TestCase(TestCase):
    def test_compare_ip_list_and_return(self):
        # Case 1: len(host_list) > len(ip_list) (Duplicate IPs)
        host_list = [{"bk_host_innerip": "1.1.1.1"}, {"bk_host_innerip": "1.1.1.1"}]
        ip_list = ["1.1.1.1"]
        with self.assertRaises(Exception):
            compare_ip_list_and_return(host_list, ip_list)

        result = compare_ip_list_and_return(host_list, ip_list, raise_exception=False)
        self.assertEqual(result, ["1.1.1.1"])

        # Case 2: len(host_list) < len(ip_list) (Missing IPs)
        host_list = [{"bk_host_innerip": "1.1.1.1"}]
        ip_list = ["1.1.1.1", "2.2.2.2"]
        result = compare_ip_list_and_return(host_list, ip_list)
        self.assertEqual(result, {"2.2.2.2"})

        # Case 3: Equal
        host_list = [{"bk_host_innerip": "1.1.1.1"}]
        ip_list = ["1.1.1.1"]
        result = compare_ip_list_and_return(host_list, ip_list)
        self.assertEqual(result, set())

    @mock.patch("pipeline_plugins.components.utils.sites.open.utils.cmdb.get_business_host_topo")
    def test_get_ipv6_info_list(self, mock_get_topo):
        tenant_id = "tenant"
        username = "user"
        biz_cc_id = 1
        ipv6_list = ["2001:db8::1"]

        # Case 1: Success
        mock_get_topo.return_value = [
            {"host": {"bk_host_innerip_v6": "2001:db8::1", "bk_host_id": 1, "bk_cloud_id": 0}, "set": [], "module": []}
        ]
        result, data = get_ipv6_info_list(tenant_id, username, biz_cc_id, ipv6_list)
        self.assertTrue(result)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["InnerIP"], "2001:db8::1")

        # Case 2: Mismatch
        mock_get_topo.return_value = []
        result, data = get_ipv6_info_list(tenant_id, username, biz_cc_id, ipv6_list)
        self.assertFalse(result)
        self.assertEqual(data, {"2001:db8::1"})

    @mock.patch("pipeline_plugins.components.utils.sites.open.utils.cmdb.get_business_host_topo")
    def test_get_ipv4_info_list(self, mock_get_topo):
        tenant_id = "tenant"
        username = "user"
        biz_cc_id = 1
        ipv4_list = ["1.1.1.1"]

        # Case 0: Empty list
        result, data = get_ipv4_info_list(tenant_id, username, biz_cc_id, [])
        self.assertTrue(result)
        self.assertEqual(data, [])

        # Case 1: Success
        mock_get_topo.return_value = [
            {"host": {"bk_host_innerip": "1.1.1.1", "bk_host_id": 1, "bk_cloud_id": 0}, "set": [], "module": []}
        ]
        result, data = get_ipv4_info_list(tenant_id, username, biz_cc_id, ipv4_list)
        self.assertTrue(result)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["InnerIP"], "1.1.1.1")

        # Case 2: Mismatch
        mock_get_topo.return_value = []
        result, data = get_ipv4_info_list(tenant_id, username, biz_cc_id, ipv4_list)
        self.assertFalse(result)
        self.assertEqual(data, {"1.1.1.1"})

    @mock.patch("pipeline_plugins.components.utils.sites.open.utils.cmdb.get_business_host_topo")
    def test_get_ipv4_info_list_with_cloud_id(self, mock_get_topo):
        tenant_id = "tenant"
        username = "user"
        biz_cc_id = 1
        ipv4_list_with_cloud_id = ["0:1.1.1.1"]

        # Case 0: Empty
        result, data = get_ipv4_info_list_with_cloud_id(tenant_id, username, biz_cc_id, [])
        self.assertTrue(result)
        self.assertEqual(data, [])

        # Case 1: Success
        mock_get_topo.return_value = [
            {"host": {"bk_host_innerip": "1.1.1.1", "bk_host_id": 1, "bk_cloud_id": 0}, "set": [], "module": []}
        ]
        result, data = get_ipv4_info_list_with_cloud_id(tenant_id, username, biz_cc_id, ipv4_list_with_cloud_id)
        self.assertTrue(result)
        self.assertEqual(len(data), 1)

        # Case 2: Mismatch (Cloud ID mismatch or IP missing)
        mock_get_topo.return_value = [
            {
                "host": {"bk_host_innerip": "1.1.1.1", "bk_host_id": 1, "bk_cloud_id": 1},  # Different cloud ID
                "set": [],
                "module": [],
            }
        ]
        result, data = get_ipv4_info_list_with_cloud_id(tenant_id, username, biz_cc_id, ipv4_list_with_cloud_id)
        self.assertFalse(result)

    @mock.patch("pipeline_plugins.components.utils.sites.open.utils.cmdb.get_business_host_topo")
    def test_get_ipv6_info_list_with_cloud_id(self, mock_get_topo):
        tenant_id = "tenant"
        username = "user"
        biz_cc_id = 1
        ipv6_list_with_cloud_id = ["0:[2001:db8::1]"]

        # Case 0: Empty
        result, data = get_ipv6_info_list_with_cloud_id(tenant_id, username, biz_cc_id, [])
        self.assertTrue(result)
        self.assertEqual(data, [])

        # Case 1: Success
        mock_get_topo.return_value = [
            {"host": {"bk_host_innerip_v6": "2001:db8::1", "bk_host_id": 1, "bk_cloud_id": 0}, "set": [], "module": []}
        ]
        result, data = get_ipv6_info_list_with_cloud_id(tenant_id, username, biz_cc_id, ipv6_list_with_cloud_id)
        self.assertTrue(result)
        self.assertEqual(len(data), 1)

        # Case 2: Mismatch
        mock_get_topo.return_value = []
        result, data = get_ipv6_info_list_with_cloud_id(tenant_id, username, biz_cc_id, ipv6_list_with_cloud_id)
        self.assertFalse(result)

    @mock.patch("pipeline_plugins.components.utils.sites.open.utils.cmdb.get_business_host_topo")
    def test_get_host_info_list(self, mock_get_topo):
        tenant_id = "tenant"
        username = "user"
        biz_cc_id = 1
        host_id_list = [1]

        # Case 1: Success
        mock_get_topo.return_value = [
            {"host": {"bk_host_innerip": "1.1.1.1", "bk_host_id": 1, "bk_cloud_id": 0}, "set": [], "module": []}
        ]
        result, data = get_host_info_list(tenant_id, username, biz_cc_id, host_id_list)
        self.assertTrue(result)
        self.assertEqual(len(data), 1)

        # Case 2: Mismatch
        mock_get_topo.return_value = []
        result, data = get_host_info_list(tenant_id, username, biz_cc_id, host_id_list)
        self.assertFalse(result)

        # Case 3: No innerip, use v6
        mock_get_topo.return_value = [
            {
                "host": {"bk_host_innerip": "", "bk_host_innerip_v6": "2001::1", "bk_host_id": 1, "bk_cloud_id": 0},
                "set": [],
                "module": [],
            }
        ]
        result, data = get_host_info_list(tenant_id, username, biz_cc_id, host_id_list)
        self.assertTrue(result)
        self.assertEqual(data[0]["InnerIP"], "2001::1")

    @mock.patch("pipeline_plugins.components.utils.sites.open.utils.get_ipv4_info_list_with_cloud_id")
    @mock.patch("pipeline_plugins.components.utils.sites.open.utils.get_host_info_list")
    @mock.patch("pipeline_plugins.components.utils.sites.open.utils.get_ipv4_info_list")
    @mock.patch("pipeline_plugins.components.utils.sites.open.utils.get_ipv6_info_list_with_cloud_id")
    @mock.patch("pipeline_plugins.components.utils.sites.open.utils.get_ipv6_info_list")
    @mock.patch("pipeline_plugins.components.utils.sites.open.utils.extract_ip_from_ip_str")
    def test_cc_get_ips_info_by_str_ipv6(
        self, mock_extract, mock_get_ipv6, mock_get_ipv6_cloud, mock_get_ipv4, mock_get_host, mock_get_ipv4_cloud
    ):
        mock_extract.return_value = ([], [], [], [], [])

        # All calls return success
        mock_get_ipv6.return_value = (True, [])
        mock_get_ipv6_cloud.return_value = (True, [])
        mock_get_ipv4.return_value = (True, [])
        mock_get_host.return_value = (True, [])
        mock_get_ipv4_cloud.return_value = (True, [])

        result = cc_get_ips_info_by_str_ipv6("tenant", "user", 1, "ip_str")
        self.assertTrue(result["result"])

        # Fail cases
        mock_get_ipv6.return_value = (False, [])
        result = cc_get_ips_info_by_str_ipv6("tenant", "user", 1, "ip_str")
        self.assertFalse(result["result"])
        mock_get_ipv6.return_value = (True, [])

        mock_get_ipv6_cloud.return_value = (False, [])
        result = cc_get_ips_info_by_str_ipv6("tenant", "user", 1, "ip_str")
        self.assertFalse(result["result"])
        mock_get_ipv6_cloud.return_value = (True, [])

        mock_get_ipv4.return_value = (False, [])
        result = cc_get_ips_info_by_str_ipv6("tenant", "user", 1, "ip_str")
        self.assertFalse(result["result"])
        mock_get_ipv4.return_value = (True, [])

        mock_get_host.return_value = (False, [])
        result = cc_get_ips_info_by_str_ipv6("tenant", "user", 1, "ip_str")
        self.assertFalse(result["result"])
        mock_get_host.return_value = (True, [])

        mock_get_ipv4_cloud.return_value = (False, [])
        result = cc_get_ips_info_by_str_ipv6("tenant", "user", 1, "ip_str")
        self.assertFalse(result["result"])

    @mock.patch("pipeline_plugins.components.utils.sites.open.utils.cmdb.get_business_host_topo")
    def test_cc_get_ips_info_by_str(self, mock_get_topo):
        tenant_id = "tenant"
        username = "user"
        biz_cc_id = 1

        # Mock CMDB return
        mock_get_topo.return_value = [
            {
                "host": {"bk_host_innerip": "1.1.1.1", "bk_host_id": 1, "bk_cloud_id": 0},
                "set": [{"bk_set_name": "set1", "bk_set_id": 1}],
                "module": [{"bk_module_name": "mod1", "bk_module_id": 1}],
            }
        ]

        # Case 1: Simple IP
        result = cc_get_ips_info_by_str(tenant_id, username, biz_cc_id, "1.1.1.1")
        self.assertTrue(result["result"])
        self.assertEqual(len(result["ip_result"]), 1)

        # Case 2: Cloud ID:IP
        result = cc_get_ips_info_by_str(tenant_id, username, biz_cc_id, "0:1.1.1.1")
        self.assertTrue(result["result"])
        self.assertEqual(len(result["ip_result"]), 1)

        # Case 3: Set|Module|IP
        result = cc_get_ips_info_by_str(tenant_id, username, biz_cc_id, "set1|mod1|1.1.1.1")
        self.assertTrue(result["result"])
        self.assertEqual(len(result["ip_result"]), 1)

    @mock.patch("pipeline_plugins.components.utils.sites.open.utils.find_module_with_relation")
    def test_get_module_id_list_by_name(self, mock_find):
        mock_find.return_value = [1, 2]
        set_list = [{"bk_set_id": 1}]
        service_template_list = [{"id": 1}]

        result = get_module_id_list_by_name("tenant", 1, "user", set_list, service_template_list)
        self.assertEqual(result, [1, 2])

    def test_get_nodeman_job_url(self):
        url = get_nodeman_job_url(1, 1)
        self.assertTrue("task-history/1/log/host|instance|host|1" in url)

    def test_get_difference_ip_list(self):
        diff = get_difference_ip_list(["1.1.1.1", "2.2.2.2"], ["1.1.1.1"])
        self.assertEqual(diff, {"2.2.2.2"})

    def test_get_repeat_ip(self):
        ip_list = [{"ip": "1.1.1.1", "bk_cloud_id": 0}, {"ip": "1.1.1.1", "bk_cloud_id": 1}]
        msg = get_repeat_ip(ip_list)
        self.assertTrue("1.1.1.1" in msg)
        self.assertTrue("0" in msg)
        self.assertTrue("1" in msg)

    @mock.patch("pipeline_plugins.components.utils.sites.open.utils.cc_get_ips_info_by_str")
    def test_get_biz_ip_from_frontend(self, mock_cc_get):
        data = mock.Mock()
        data.outputs.ex_data = ""
        logger = mock.Mock()

        # Case 1: Empty IP
        result, ip_list = get_biz_ip_from_frontend("tenant", "", "user", 1, data, logger)
        self.assertTrue(result)
        self.assertEqual(ip_list, [])

        # Case 2: Across biz
        result, ip_list = get_biz_ip_from_frontend("tenant", "0:1.1.1.1", "user", 1, data, logger, is_across=True)
        self.assertTrue(result)
        self.assertEqual(len(ip_list), 1)

        # Case 3: Normal valid
        mock_cc_get.return_value = {"ip_result": [{"InnerIP": "1.1.1.1", "Source": 0}]}
        result, ip_list = get_biz_ip_from_frontend("tenant", "1.1.1.1", "user", 1, data, logger)
        self.assertTrue(result)
        self.assertEqual(len(ip_list), 1)

        # Case 4: Invalid IP
        mock_cc_get.return_value = {"ip_result": []}
        result, ip_list = get_biz_ip_from_frontend("tenant", "1.1.1.1", "user", 1, data, logger)
        self.assertFalse(result)
        self.assertNotEqual(data.outputs.ex_data, "")

    @mock.patch("pipeline_plugins.components.utils.sites.open.utils.cc_get_ips_info_by_str")
    def test_get_biz_ip_from_frontend_hybrid(self, mock_cc_get):
        data = mock.Mock()
        data.outputs.ex_data = ""

        # Case 1: Only cloud IP
        result, ip_list = get_biz_ip_from_frontend_hybrid("tenant", "user", "0:1.1.1.1", 1, data)
        self.assertTrue(result)
        self.assertEqual(len(ip_list), 1)
        self.assertEqual(ip_list[0]["ip"], "1.1.1.1")

        # Case 2: Hybrid valid
        mock_cc_get.return_value = {"ip_result": [{"InnerIP": "2.2.2.2", "Source": 0}]}
        result, ip_list = get_biz_ip_from_frontend_hybrid("tenant", "user", "0:1.1.1.1,2.2.2.2", 1, data)
        self.assertTrue(result)
        self.assertEqual(len(ip_list), 2)

        # Case 3: Invalid
        mock_cc_get.return_value = {"ip_result": []}
        result, ip_list = get_biz_ip_from_frontend_hybrid("tenant", "user", "2.2.2.2", 1, data)
        self.assertFalse(result)
