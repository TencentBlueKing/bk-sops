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

from pipeline_plugins.components.collections.sites.open.cc.base import cc_get_host_id_by_innerip_and_cloudid


class CCGetHostIdByCloudIdInnerIpTestCase(TestCase):
    def setUp(self):
        self.executor = "executor_token"
        self.bk_biz_id = "bk_biz_id_token"
        self.supplier_account = "supplier_account_token"
        self.ip_str = "1.1.1.1"
        self.tenant_id = "system"

    def test__get_business_host_return_empty(self):
        mock_cmdb = MagicMock()
        mock_cmdb.get_business_host = MagicMock(return_value=[])
        with patch("pipeline_plugins.components.collections.sites.open.cc.base.cmdb", mock_cmdb):
            data = cc_get_host_id_by_innerip_and_cloudid(self.tenant_id, self.executor, self.bk_biz_id, self.ip_str)

        mock_cmdb.get_business_host.assert_called_once_with(
            self.tenant_id, self.executor, self.bk_biz_id, ["bk_host_id", "bk_host_innerip"], [self.ip_str], None
        )
        self.assertFalse(data["result"])
        self.assertEqual(
            data["message"], "IP ['1.1.1.1'] 在本业务下不存在: 请检查配置, 修复后重新执行 | cc_get_host_id_by_innerip_and_cloudid"
        )

    def test__return_host_list_gt_ip_list(self):
        mock_cmdb = MagicMock()
        mock_cmdb.get_business_host = MagicMock(
            return_value=[
                {"bk_host_innerip": "1.1.1.1"},
                {"bk_host_innerip": "1.1.1.1"},
            ]
        )
        with patch("pipeline_plugins.components.collections.sites.open.cc.base.cmdb", mock_cmdb):
            data = cc_get_host_id_by_innerip_and_cloudid(self.tenant_id, self.executor, self.bk_biz_id, self.ip_str)

        mock_cmdb.get_business_host.assert_called_once_with(
            self.tenant_id, self.executor, self.bk_biz_id, ["bk_host_id", "bk_host_innerip"], [self.ip_str], None
        )
        self.assertFalse(data["result"])
        self.assertEqual(
            data["message"], "IP [1.1.1.1] 在本业务下重复: 请检查配置, 修复后重新执行 | cc_get_host_id_by_innerip_and_cloudid"
        )

    def test__return_host_list_lt_cloudid_with_ip_list(self):
        self.ip_str = "0:1.1.1.1"
        mock_cmdb = MagicMock()
        mock_cmdb.get_business_host = MagicMock(return_value=[])
        with patch("pipeline_plugins.components.collections.sites.open.cc.base.cmdb", mock_cmdb):
            data = cc_get_host_id_by_innerip_and_cloudid(self.tenant_id, self.executor, self.bk_biz_id, self.ip_str)

        mock_cmdb.get_business_host.assert_called_once_with(
            self.tenant_id,
            self.executor,
            self.bk_biz_id,
            ["bk_host_id", "bk_host_innerip", "bk_cloud_id"],
            [self.ip_str.split(":")[1]],
            0,
        )
        self.assertFalse(data["result"])
        self.assertEqual(
            data["message"], "IP ['1.1.1.1'] 在本业务下不存在: 请检查配置, 修复后重新执行 | cc_get_host_id_by_innerip_and_cloudid"
        )

    def test__ip_normal(self):
        mock_cmdb = MagicMock()
        mock_cmdb.get_business_host = MagicMock(
            return_value=[
                {"bk_host_innerip": "1.1.1.1", "bk_host_id": 1},
            ]
        )
        with patch("pipeline_plugins.components.collections.sites.open.cc.base.cmdb", mock_cmdb):
            data = cc_get_host_id_by_innerip_and_cloudid(self.tenant_id, self.executor, self.bk_biz_id, self.ip_str)

        mock_cmdb.get_business_host.assert_called_once_with(
            self.tenant_id, self.executor, self.bk_biz_id, ["bk_host_id", "bk_host_innerip"], [self.ip_str], None
        )
        self.assertTrue(data["result"])
        self.assertEqual(data["data"], ["1"])

    def test__cloudid_with_ip_normal(self):
        self.ip_str = "0:1.1.1.1"
        mock_cmdb = MagicMock()
        mock_cmdb.get_business_host = MagicMock(
            return_value=[
                {"bk_host_innerip": "1.1.1.1", "bk_host_id": 1, "bk_cloud_id": 0},
            ]
        )
        with patch("pipeline_plugins.components.collections.sites.open.cc.base.cmdb", mock_cmdb):
            data = cc_get_host_id_by_innerip_and_cloudid(self.tenant_id, self.executor, self.bk_biz_id, self.ip_str)

        mock_cmdb.get_business_host.assert_called_once_with(
            self.tenant_id,
            self.executor,
            self.bk_biz_id,
            ["bk_host_id", "bk_host_innerip", "bk_cloud_id"],
            [self.ip_str.split(":")[1]],
            0,
        )
        self.assertTrue(data["result"])
        self.assertEqual(data["data"], ["1"])
