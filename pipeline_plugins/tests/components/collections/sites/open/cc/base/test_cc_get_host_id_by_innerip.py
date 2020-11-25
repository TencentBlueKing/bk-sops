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

from pipeline_plugins.components.collections.sites.open.cc.base import cc_get_host_id_by_innerip


class CCGetHostIdByInnerIpTestCase(TestCase):
    def setUp(self):
        self.executor = "executor_token"
        self.bk_biz_id = "bk_biz_id_token"
        self.ip_list = "ip_list_token"
        self.supplier_account = "supplier_account_token"
        self.ip_list = ["1.1.1.1", "2.2.2.2", "3.3.3.3"]

    def test__get_business_host_return_empty(self):
        mock_cmdb = MagicMock()
        mock_cmdb.get_business_host = MagicMock(return_value=[])
        with patch("pipeline_plugins.components.collections.sites.open.cc.base.cmdb", mock_cmdb):
            data = cc_get_host_id_by_innerip(self.executor, self.bk_biz_id, self.ip_list, self.supplier_account)

        mock_cmdb.get_business_host.assert_called_once_with(
            self.executor, self.bk_biz_id, self.supplier_account, ["bk_host_id", "bk_host_innerip"], self.ip_list
        )
        self.assertFalse(data["result"])
        self.assertEqual(data["message"], "list_biz_hosts query failed, return empty list")

    def test__return_host_list_gt_ip_list(self):
        mock_cmdb = MagicMock()
        mock_cmdb.get_business_host = MagicMock(
            return_value=[
                {"bk_host_innerip": "1.1.1.1"},
                {"bk_host_innerip": "1.1.1.1"},
                {"bk_host_innerip": "2.2.2.2"},
                {"bk_host_innerip": "2.2.2.2"},
                {"bk_host_innerip": "3.3.3.3"},
            ]
        )
        with patch("pipeline_plugins.components.collections.sites.open.cc.base.cmdb", mock_cmdb):
            data = cc_get_host_id_by_innerip(self.executor, self.bk_biz_id, self.ip_list, self.supplier_account)

        mock_cmdb.get_business_host.assert_called_once_with(
            self.executor, self.bk_biz_id, self.supplier_account, ["bk_host_id", "bk_host_innerip"], self.ip_list
        )
        self.assertFalse(data["result"])
        self.assertEqual(data["message"], "mutiple same innerip host found: 1.1.1.1, 2.2.2.2")

    def test__return_host_list_lt_ip_list(self):
        mock_cmdb = MagicMock()
        mock_cmdb.get_business_host = MagicMock(
            return_value=[{"bk_host_innerip": "1.1.1.1"}, {"bk_host_innerip": "2.2.2.2"}]
        )
        with patch("pipeline_plugins.components.collections.sites.open.cc.base.cmdb", mock_cmdb):
            data = cc_get_host_id_by_innerip(self.executor, self.bk_biz_id, self.ip_list, self.supplier_account)

        mock_cmdb.get_business_host.assert_called_once_with(
            self.executor, self.bk_biz_id, self.supplier_account, ["bk_host_id", "bk_host_innerip"], self.ip_list
        )
        self.assertFalse(data["result"])
        self.assertEqual(data["message"], "ip not found in business: 3.3.3.3")

    def test__normal(self):
        mock_cmdb = MagicMock()
        mock_cmdb.get_business_host = MagicMock(
            return_value=[
                {"bk_host_innerip": "1.1.1.1", "bk_host_id": 1},
                {"bk_host_innerip": "2.2.2.2", "bk_host_id": 2},
                {"bk_host_innerip": "3.3.3.3", "bk_host_id": 3},
            ]
        )
        with patch("pipeline_plugins.components.collections.sites.open.cc.base.cmdb", mock_cmdb):
            data = cc_get_host_id_by_innerip(self.executor, self.bk_biz_id, self.ip_list, self.supplier_account)

        mock_cmdb.get_business_host.assert_called_once_with(
            self.executor, self.bk_biz_id, self.supplier_account, ["bk_host_id", "bk_host_innerip"], self.ip_list
        )
        self.assertTrue(data["result"])
        self.assertEqual(data["data"], ["1", "2", "3"])
