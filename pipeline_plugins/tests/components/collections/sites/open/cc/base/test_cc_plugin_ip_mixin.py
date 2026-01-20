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
from mock import patch

from pipeline_plugins.components.collections.sites.open.cc.base import CCPluginIPMixin


class CCPluginIPMixinTestCase(TestCase):
    def setUp(self):
        self.tenant_id = "system"
        self.executor = "executor_token"
        self.biz_cc_id = 2
        self.mixin = CCPluginIPMixin()

    @patch("pipeline_plugins.components.collections.sites.open.cc.base.settings")
    @patch("pipeline_plugins.components.collections.sites.open.cc.base.cc_get_host_by_innerip_with_ipv6")
    def test__get_host_list_with_ipv6_enabled_success(self, mock_cc_get_host, mock_settings):
        mock_settings.ENABLE_IPV6 = True
        mock_cc_get_host.return_value = {
            "result": True,
            "data": [{"bk_host_id": 1}, {"bk_host_id": 2}, {"bk_host_id": 3}],
        }

        ip_str = "1.1.1.1,2.2.2.2"
        result = self.mixin.get_host_list(self.tenant_id, self.executor, self.biz_cc_id, ip_str)

        self.assertTrue(result["result"])
        self.assertEqual(result["data"], ["1", "2", "3"])
        mock_cc_get_host.assert_called_once_with(self.tenant_id, self.executor, self.biz_cc_id, ip_str)

    @patch("pipeline_plugins.components.collections.sites.open.cc.base.settings")
    @patch("pipeline_plugins.components.collections.sites.open.cc.base.cc_get_host_by_innerip_with_ipv6")
    def test__get_host_list_with_ipv6_enabled_fail(self, mock_cc_get_host, mock_settings):
        mock_settings.ENABLE_IPV6 = True
        mock_cc_get_host.return_value = {"result": False, "message": "host not found"}

        ip_str = "1.1.1.1"
        result = self.mixin.get_host_list(self.tenant_id, self.executor, self.biz_cc_id, ip_str)

        self.assertFalse(result["result"])
        self.assertEqual(result["message"], "host not found")

    @patch("pipeline_plugins.components.collections.sites.open.cc.base.settings")
    @patch("pipeline_plugins.components.collections.sites.open.cc.base.cc_get_host_id_by_innerip")
    @patch("pipeline_plugins.components.collections.sites.open.cc.base.get_ip_by_regex")
    def test__get_host_list_without_ipv6(self, mock_get_ip, mock_cc_get_host, mock_settings):
        mock_settings.ENABLE_IPV6 = False
        mock_get_ip.return_value = ["1.1.1.1", "2.2.2.2"]
        mock_cc_get_host.return_value = {"result": True, "data": ["1", "2"]}

        ip_str = "1.1.1.1,2.2.2.2"
        result = self.mixin.get_host_list(self.tenant_id, self.executor, self.biz_cc_id, ip_str)

        self.assertTrue(result["result"])
        self.assertEqual(result["data"], ["1", "2"])
        mock_get_ip.assert_called_once_with(ip_str)

    @patch("pipeline_plugins.components.collections.sites.open.cc.base.settings")
    @patch("pipeline_plugins.components.collections.sites.open.cc.base.cc_get_ips_info_by_str_ipv6")
    def test__get_ip_info_list_with_ipv6_enabled(self, mock_cc_get_ips_info, mock_settings):
        mock_settings.ENABLE_IPV6 = True
        expected_result = {
            "result": True,
            "ip_result": [{"ip": "1.1.1.1"}],
            "ip_count": 1,
            "invalid_ip": [],
        }
        mock_cc_get_ips_info.return_value = expected_result

        ip_str = "1.1.1.1"
        result = self.mixin.get_ip_info_list(self.tenant_id, self.executor, self.biz_cc_id, ip_str)

        self.assertEqual(result, expected_result)
        mock_cc_get_ips_info.assert_called_once_with(self.tenant_id, self.executor, self.biz_cc_id, ip_str)

    @patch("pipeline_plugins.components.collections.sites.open.cc.base.settings")
    @patch("pipeline_plugins.components.collections.sites.open.cc.base.cc_get_ips_info_by_str")
    def test__get_ip_info_list_without_ipv6(self, mock_cc_get_ips_info, mock_settings):
        mock_settings.ENABLE_IPV6 = False
        expected_result = {
            "result": True,
            "ip_result": [{"ip": "1.1.1.1"}],
            "ip_count": 1,
            "invalid_ip": [],
        }
        mock_cc_get_ips_info.return_value = expected_result

        ip_str = "1.1.1.1"
        result = self.mixin.get_ip_info_list(self.tenant_id, self.executor, self.biz_cc_id, ip_str)

        self.assertEqual(result, expected_result)
        mock_cc_get_ips_info.assert_called_once_with(self.tenant_id, self.executor, self.biz_cc_id, ip_str)

    @patch("pipeline_plugins.components.collections.sites.open.cc.base.settings")
    @patch("pipeline_plugins.components.collections.sites.open.cc.base.cmdb")
    @patch("pipeline_plugins.components.collections.sites.open.cc.base.get_ip_by_regex")
    def test__get_host_topo_without_ipv6(self, mock_get_ip, mock_cmdb, mock_settings):
        mock_settings.ENABLE_IPV6 = False
        mock_get_ip.return_value = ["1.1.1.1", "2.2.2.2"]
        mock_cmdb.get_business_host_topo.return_value = {"result": True, "data": []}

        ip_str = "1.1.1.1,2.2.2.2"
        host_attrs = ["bk_host_id", "bk_host_innerip"]
        result = self.mixin.get_host_topo(self.tenant_id, self.executor, self.biz_cc_id, host_attrs, ip_str)

        self.assertTrue(result["result"])
        mock_cmdb.get_business_host_topo.assert_called_once_with(
            self.tenant_id, self.executor, self.biz_cc_id, host_attrs, ["1.1.1.1", "2.2.2.2"]
        )

    @patch("pipeline_plugins.components.collections.sites.open.cc.base.settings")
    @patch("pipeline_plugins.components.collections.sites.open.cc.base.cmdb")
    @patch("pipeline_plugins.components.collections.sites.open.cc.base.get_ip_by_regex_type")
    @patch("pipeline_plugins.components.collections.sites.open.cc.base.ipv6_pattern")
    def test__get_host_topo_with_ipv6_address(self, mock_ipv6_pattern, mock_get_ip_type, mock_cmdb, mock_settings):
        mock_settings.ENABLE_IPV6 = True
        mock_ipv6_pattern.match.return_value = True
        mock_get_ip_type.return_value = (["fe80::1", "fe80::2"], "")
        mock_cmdb.get_business_host_topo.return_value = {"result": True, "data": []}

        ip_str = "fe80::1,fe80::2"
        host_attrs = ["bk_host_id"]
        result = self.mixin.get_host_topo(self.tenant_id, self.executor, self.biz_cc_id, host_attrs, ip_str)

        self.assertTrue(result["result"])
        call_args = mock_cmdb.get_business_host_topo.call_args
        self.assertEqual(call_args[1]["ip_list"], None)
        self.assertIn("host_property_filter", call_args[1]["property_filters"])

    @patch("pipeline_plugins.components.collections.sites.open.cc.base.settings")
    @patch("pipeline_plugins.components.collections.sites.open.cc.base.cmdb")
    @patch("pipeline_plugins.components.collections.sites.open.cc.base.get_ip_by_regex_type")
    @patch("pipeline_plugins.components.collections.sites.open.cc.base.ipv6_pattern")
    @patch("pipeline_plugins.components.collections.sites.open.cc.base.ip_pattern")
    def test__get_host_topo_with_ipv4_address(
        self, mock_ip_pattern, mock_ipv6_pattern, mock_get_ip_type, mock_cmdb, mock_settings
    ):
        mock_settings.ENABLE_IPV6 = True
        mock_ipv6_pattern.match.return_value = False
        mock_ip_pattern.match.return_value = True
        mock_get_ip_type.return_value = (["1.1.1.1", "2.2.2.2"], "")
        mock_cmdb.get_business_host_topo.return_value = {"result": True, "data": []}

        ip_str = "1.1.1.1,2.2.2.2"
        host_attrs = ["bk_host_id"]
        result = self.mixin.get_host_topo(self.tenant_id, self.executor, self.biz_cc_id, host_attrs, ip_str)

        self.assertTrue(result["result"])
        call_args = mock_cmdb.get_business_host_topo.call_args
        self.assertEqual(call_args[1]["ip_list"], None)
        property_filters = call_args[1]["property_filters"]
        self.assertIn("host_property_filter", property_filters)
        self.assertEqual(property_filters["host_property_filter"]["rules"][0]["field"], "bk_host_innerip")

    @patch("pipeline_plugins.components.collections.sites.open.cc.base.settings")
    @patch("pipeline_plugins.components.collections.sites.open.cc.base.cmdb")
    @patch("pipeline_plugins.components.collections.sites.open.cc.base.get_ip_by_regex_type")
    @patch("pipeline_plugins.components.collections.sites.open.cc.base.ipv6_pattern")
    @patch("pipeline_plugins.components.collections.sites.open.cc.base.ip_pattern")
    def test__get_host_topo_with_host_id(
        self, mock_ip_pattern, mock_ipv6_pattern, mock_get_ip_type, mock_cmdb, mock_settings
    ):
        mock_settings.ENABLE_IPV6 = True
        mock_ipv6_pattern.match.return_value = False
        mock_ip_pattern.match.return_value = False
        mock_get_ip_type.return_value = (["123", "456"], "")
        mock_cmdb.get_business_host_topo.return_value = {"result": True, "data": []}

        ip_str = "123"
        host_attrs = ["bk_host_id"]
        result = self.mixin.get_host_topo(self.tenant_id, self.executor, self.biz_cc_id, host_attrs, ip_str)

        self.assertTrue(result["result"])
        call_args = mock_cmdb.get_business_host_topo.call_args
        self.assertEqual(call_args[1]["ip_list"], None)
        property_filters = call_args[1]["property_filters"]
        self.assertIn("host_property_filter", property_filters)
        self.assertEqual(property_filters["host_property_filter"]["rules"][0]["field"], "bk_host_id")

    @patch("pipeline_plugins.components.collections.sites.open.cc.base.settings")
    @patch("pipeline_plugins.components.collections.sites.open.cc.base.cc_get_host_by_innerip_with_ipv6")
    def test__get_host_list_with_cloud_id_ipv6_enabled(self, mock_cc_get_host, mock_settings):
        mock_settings.ENABLE_IPV6 = True
        mock_cc_get_host.return_value = {
            "result": True,
            "data": [{"bk_host_id": 1}, {"bk_host_id": 2}],
        }

        ip_str = "1.1.1.1"
        result = self.mixin.get_host_list_with_cloud_id(self.tenant_id, self.executor, self.biz_cc_id, ip_str)

        self.assertTrue(result["result"])
        self.assertEqual(result["data"], ["1", "2"])

    @patch("pipeline_plugins.components.collections.sites.open.cc.base.settings")
    @patch("pipeline_plugins.components.collections.sites.open.cc.base.cc_get_host_id_by_innerip_and_cloudid")
    def test__get_host_list_with_cloud_id_ipv6_disabled(self, mock_cc_get_host, mock_settings):
        mock_settings.ENABLE_IPV6 = False
        mock_cc_get_host.return_value = {"result": True, "data": ["1", "2"]}

        ip_str = "0:1.1.1.1"
        result = self.mixin.get_host_list_with_cloud_id(self.tenant_id, self.executor, self.biz_cc_id, ip_str)

        self.assertTrue(result["result"])
        self.assertEqual(result["data"], ["1", "2"])
        mock_cc_get_host.assert_called_once_with(self.tenant_id, self.executor, self.biz_cc_id, ip_str)
