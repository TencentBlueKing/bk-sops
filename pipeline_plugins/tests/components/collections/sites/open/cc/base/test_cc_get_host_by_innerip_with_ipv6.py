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

from pipeline_plugins.components.collections.sites.open.cc.base import cc_get_host_by_innerip_with_ipv6


class CCGetHostByInnerIpWithIpv6TestCase(TestCase):
    def setUp(self):
        self.executor = "executor_token"
        self.bk_biz_id = "bk_biz_id_token"
        self.tenant_id = "system"
        self.ip_str = "1.1.1.1,2.2.2.2"

    @patch("pipeline_plugins.components.collections.sites.open.cc.base.get_ipv6_host_list")
    @patch("pipeline_plugins.components.collections.sites.open.cc.base.get_ipv6_host_list_with_cloud_list")
    @patch("pipeline_plugins.components.collections.sites.open.cc.base.get_ipv4_host_list")
    @patch("pipeline_plugins.components.collections.sites.open.cc.base.get_ipv4_host_with_cloud_list")
    @patch("pipeline_plugins.components.collections.sites.open.cc.base.extract_ip_from_ip_str")
    def test__ipv6_host_list_return_fail(
        self,
        mock_extract_ip,
        mock_get_ipv4_with_cloud,
        mock_get_ipv4,
        mock_get_ipv6_with_cloud,
        mock_get_ipv6,
    ):
        mock_extract_ip.return_value = ([], ["1.1.1.1"], [], [], [])
        mock_get_ipv6.return_value = {"result": False, "message": "ipv6 error"}

        result = cc_get_host_by_innerip_with_ipv6(self.tenant_id, self.executor, self.bk_biz_id, self.ip_str)

        self.assertFalse(result["result"])
        self.assertEqual(result["message"], "ipv6 error")
        mock_get_ipv6.assert_called_once_with(self.tenant_id, self.executor, self.bk_biz_id, [], is_biz_set=False)

    @patch("pipeline_plugins.components.collections.sites.open.cc.base.get_ipv6_host_list")
    @patch("pipeline_plugins.components.collections.sites.open.cc.base.get_ipv6_host_list_with_cloud_list")
    @patch("pipeline_plugins.components.collections.sites.open.cc.base.get_ipv4_host_list")
    @patch("pipeline_plugins.components.collections.sites.open.cc.base.get_ipv4_host_with_cloud_list")
    @patch("pipeline_plugins.components.collections.sites.open.cc.base.extract_ip_from_ip_str")
    def test__ipv6_with_cloud_return_fail(
        self,
        mock_extract_ip,
        mock_get_ipv4_with_cloud,
        mock_get_ipv4,
        mock_get_ipv6_with_cloud,
        mock_get_ipv6,
    ):
        mock_extract_ip.return_value = ([], ["1.1.1.1"], [], [], [])
        mock_get_ipv6.return_value = {"result": True, "data": []}
        mock_get_ipv6_with_cloud.return_value = {"result": False, "message": "ipv6 with cloud error"}

        result = cc_get_host_by_innerip_with_ipv6(self.tenant_id, self.executor, self.bk_biz_id, self.ip_str)

        self.assertFalse(result["result"])
        self.assertEqual(result["message"], "ipv6 with cloud error")

    @patch("pipeline_plugins.components.collections.sites.open.cc.base.get_ipv6_host_list")
    @patch("pipeline_plugins.components.collections.sites.open.cc.base.get_ipv6_host_list_with_cloud_list")
    @patch("pipeline_plugins.components.collections.sites.open.cc.base.get_ipv4_host_list")
    @patch("pipeline_plugins.components.collections.sites.open.cc.base.get_ipv4_host_with_cloud_list")
    @patch("pipeline_plugins.components.collections.sites.open.cc.base.extract_ip_from_ip_str")
    def test__ipv4_host_list_return_fail(
        self,
        mock_extract_ip,
        mock_get_ipv4_with_cloud,
        mock_get_ipv4,
        mock_get_ipv6_with_cloud,
        mock_get_ipv6,
    ):
        mock_extract_ip.return_value = ([], ["1.1.1.1"], [], [], [])
        mock_get_ipv6.return_value = {"result": True, "data": []}
        mock_get_ipv6_with_cloud.return_value = {"result": True, "data": []}
        mock_get_ipv4.return_value = {"result": False, "message": "ipv4 error"}

        result = cc_get_host_by_innerip_with_ipv6(self.tenant_id, self.executor, self.bk_biz_id, self.ip_str)

        self.assertFalse(result["result"])
        self.assertEqual(result["message"], "ipv4 error")

    @patch("pipeline_plugins.components.collections.sites.open.cc.base.get_ipv6_host_list")
    @patch("pipeline_plugins.components.collections.sites.open.cc.base.get_ipv6_host_list_with_cloud_list")
    @patch("pipeline_plugins.components.collections.sites.open.cc.base.get_ipv4_host_list")
    @patch("pipeline_plugins.components.collections.sites.open.cc.base.get_ipv4_host_with_cloud_list")
    @patch("pipeline_plugins.components.collections.sites.open.cc.base.extract_ip_from_ip_str")
    def test__ipv4_with_cloud_return_fail(
        self,
        mock_extract_ip,
        mock_get_ipv4_with_cloud,
        mock_get_ipv4,
        mock_get_ipv6_with_cloud,
        mock_get_ipv6,
    ):
        mock_extract_ip.return_value = ([], ["1.1.1.1"], [], [], [])
        mock_get_ipv6.return_value = {"result": True, "data": []}
        mock_get_ipv6_with_cloud.return_value = {"result": True, "data": []}
        mock_get_ipv4.return_value = {"result": True, "data": []}
        mock_get_ipv4_with_cloud.return_value = {"result": False, "message": "ipv4 with cloud error"}

        result = cc_get_host_by_innerip_with_ipv6(self.tenant_id, self.executor, self.bk_biz_id, self.ip_str)

        self.assertFalse(result["result"])
        self.assertEqual(result["message"], "ipv4 with cloud error")

    @patch("pipeline_plugins.components.collections.sites.open.cc.base.get_hosts_by_hosts_ids")
    @patch("pipeline_plugins.components.collections.sites.open.cc.base.get_ipv6_host_list")
    @patch("pipeline_plugins.components.collections.sites.open.cc.base.get_ipv6_host_list_with_cloud_list")
    @patch("pipeline_plugins.components.collections.sites.open.cc.base.get_ipv4_host_list")
    @patch("pipeline_plugins.components.collections.sites.open.cc.base.get_ipv4_host_with_cloud_list")
    @patch("pipeline_plugins.components.collections.sites.open.cc.base.extract_ip_from_ip_str")
    def test__host_id_detail_return_fail(
        self,
        mock_extract_ip,
        mock_get_ipv4_with_cloud,
        mock_get_ipv4,
        mock_get_ipv6_with_cloud,
        mock_get_ipv6,
        mock_get_hosts_by_ids,
    ):
        mock_extract_ip.return_value = ([], ["1.1.1.1"], ["1", "2"], [], [])
        mock_get_ipv6.return_value = {"result": True, "data": []}
        mock_get_ipv6_with_cloud.return_value = {"result": True, "data": []}
        mock_get_ipv4.return_value = {"result": True, "data": []}
        mock_get_ipv4_with_cloud.return_value = {"result": True, "data": []}
        mock_get_hosts_by_ids.return_value = {"result": False, "message": "host id error"}

        result = cc_get_host_by_innerip_with_ipv6(
            self.tenant_id, self.executor, self.bk_biz_id, self.ip_str, host_id_detail=True
        )

        self.assertFalse(result["result"])
        self.assertEqual(result["message"], "host id error")

    @patch("pipeline_plugins.components.collections.sites.open.cc.base.get_ipv6_host_list")
    @patch("pipeline_plugins.components.collections.sites.open.cc.base.get_ipv6_host_list_with_cloud_list")
    @patch("pipeline_plugins.components.collections.sites.open.cc.base.get_ipv4_host_list")
    @patch("pipeline_plugins.components.collections.sites.open.cc.base.get_ipv4_host_with_cloud_list")
    @patch("pipeline_plugins.components.collections.sites.open.cc.base.extract_ip_from_ip_str")
    def test__normal(
        self,
        mock_extract_ip,
        mock_get_ipv4_with_cloud,
        mock_get_ipv4,
        mock_get_ipv6_with_cloud,
        mock_get_ipv6,
    ):
        mock_extract_ip.return_value = ([], ["1.1.1.1", "2.2.2.2"], ["1", "2"], [], [])
        mock_get_ipv6.return_value = {"result": True, "data": []}
        mock_get_ipv6_with_cloud.return_value = {"result": True, "data": []}
        mock_get_ipv4.return_value = {"result": True, "data": [{"bk_host_id": 10}, {"bk_host_id": 20}]}
        mock_get_ipv4_with_cloud.return_value = {"result": True, "data": []}

        result = cc_get_host_by_innerip_with_ipv6(self.tenant_id, self.executor, self.bk_biz_id, self.ip_str)

        self.assertTrue(result["result"])
        self.assertEqual(
            result["data"], [{"bk_host_id": 10}, {"bk_host_id": 20}, {"bk_host_id": "1"}, {"bk_host_id": "2"}]
        )

    @patch("pipeline_plugins.components.collections.sites.open.cc.base.get_hosts_by_hosts_ids")
    @patch("pipeline_plugins.components.collections.sites.open.cc.base.get_ipv6_host_list")
    @patch("pipeline_plugins.components.collections.sites.open.cc.base.get_ipv6_host_list_with_cloud_list")
    @patch("pipeline_plugins.components.collections.sites.open.cc.base.get_ipv4_host_list")
    @patch("pipeline_plugins.components.collections.sites.open.cc.base.get_ipv4_host_with_cloud_list")
    @patch("pipeline_plugins.components.collections.sites.open.cc.base.extract_ip_from_ip_str")
    def test__normal_with_host_id_detail(
        self,
        mock_extract_ip,
        mock_get_ipv4_with_cloud,
        mock_get_ipv4,
        mock_get_ipv6_with_cloud,
        mock_get_ipv6,
        mock_get_hosts_by_ids,
    ):
        mock_extract_ip.return_value = (
            ["fe80::1"],
            ["1.1.1.1"],
            ["1"],
            [],
            [],
        )
        mock_get_ipv6.return_value = {"result": True, "data": [{"bk_host_id": 100}]}
        mock_get_ipv6_with_cloud.return_value = {"result": True, "data": []}
        mock_get_ipv4.return_value = {"result": True, "data": [{"bk_host_id": 10}]}
        mock_get_ipv4_with_cloud.return_value = {"result": True, "data": []}
        mock_get_hosts_by_ids.return_value = {"result": True, "data": [{"bk_host_id": 1}]}

        result = cc_get_host_by_innerip_with_ipv6(
            self.tenant_id, self.executor, self.bk_biz_id, self.ip_str, host_id_detail=True
        )

        self.assertTrue(result["result"])
        self.assertEqual(
            result["data"],
            [
                {"bk_host_id": 100},
                {"bk_host_id": 10},
                {"bk_host_id": 1},
            ],
        )
        mock_get_hosts_by_ids.assert_called_once_with(self.tenant_id, self.executor, self.bk_biz_id, ["1"])
