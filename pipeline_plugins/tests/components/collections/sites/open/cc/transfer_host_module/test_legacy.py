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

from pipeline_plugins.components.collections.sites.open.cc.transfer_host_module.legacy import (
    CCTransferHostModuleComponent,
    CCTransferHostModuleService,
)


class CCTransferHostModuleServiceTestCase(TestCase):
    def setUp(self):
        self.service = CCTransferHostModuleService()
        self.service.logger = MagicMock()

    def test_inputs_format(self):
        inputs = self.service.inputs_format()
        self.assertEqual(len(inputs), 4)
        self.assertEqual(inputs[0].key, "biz_cc_id")
        self.assertEqual(inputs[1].key, "cc_host_ip")
        self.assertEqual(inputs[2].key, "cc_module_select")
        self.assertEqual(inputs[3].key, "cc_is_increment")

    def test_outputs_format(self):
        outputs = self.service.outputs_format()
        self.assertEqual(len(outputs), 0)

    @patch("pipeline_plugins.components.collections.sites.open.cc.transfer_host_module.legacy.get_client_by_username")
    def test_execute_success(self, mock_get_client):
        # 准备数据
        parent_data = MagicMock()
        parent_data.get_one_of_inputs = MagicMock(
            side_effect=lambda x, default=None: {
                "executor": "admin",
                "tenant_id": "system",
                "biz_cc_id": 2,
                "language": "zh-cn",
            }.get(x, default)
        )
        parent_data.inputs.biz_cc_id = 2

        data = MagicMock()
        data.get_one_of_inputs = MagicMock(
            side_effect=lambda x, default=None: {
                "biz_cc_id": 2,
                "cc_host_ip": "1.1.1.1",
                "cc_module_select": ["module_1", "module_2"],
                "cc_is_increment": "true",
            }.get(x, default)
        )

        # mock client
        mock_client = MagicMock()
        mock_client.api.transfer_host_module = MagicMock(return_value={"result": True})
        mock_get_client.return_value = mock_client

        # mock get_ip_info_list
        with patch.object(self.service, "get_ip_info_list") as mock_get_ip_info:
            mock_get_ip_info.return_value = {"result": True, "ip_result": [{"HostID": 100}]}

            # 执行
            result = self.service.execute(data, parent_data)

        # 断言
        self.assertTrue(result)
        mock_client.api.transfer_host_module.assert_called()

        # 验证参数
        call_args = mock_client.api.transfer_host_module.call_args[0][0]
        self.assertEqual(call_args["bk_biz_id"], 2)
        self.assertEqual(call_args["bk_host_id"], [100])
        self.assertEqual(call_args["is_increment"], True)

    @patch("pipeline_plugins.components.collections.sites.open.cc.transfer_host_module.legacy.get_client_by_username")
    def test_execute_get_ip_info_fail(self, mock_get_client):
        parent_data = MagicMock()
        parent_data.get_one_of_inputs = MagicMock(
            side_effect=lambda x, default=None: {
                "executor": "admin",
                "tenant_id": "system",
            }.get(x, default)
        )
        parent_data.inputs.biz_cc_id = 2

        data = MagicMock()
        data.get_one_of_inputs = MagicMock(
            side_effect=lambda x, default=None: {
                "biz_cc_id": 2,
                "cc_host_ip": "1.1.1.1",
            }.get(x, default)
        )

        mock_get_client.return_value = MagicMock()

        # mock get_ip_info_list fail
        with patch.object(self.service, "get_ip_info_list") as mock_get_ip_info:
            mock_get_ip_info.return_value = {"result": False, "message": "ip info error"}

            result = self.service.execute(data, parent_data)

        self.assertFalse(result)
        data.set_outputs.assert_called_with("ex_data", "ip info error")

    @patch("pipeline_plugins.components.collections.sites.open.cc.transfer_host_module.legacy.cc_handle_api_error")
    @patch("pipeline_plugins.components.collections.sites.open.cc.transfer_host_module.legacy.get_client_by_username")
    def test_execute_transfer_fail(self, mock_get_client, mock_handle_error):
        parent_data = MagicMock()
        parent_data.get_one_of_inputs = MagicMock(
            side_effect=lambda x, default=None: {
                "executor": "admin",
                "tenant_id": "system",
            }.get(x, default)
        )
        parent_data.inputs.biz_cc_id = 2

        data = MagicMock()
        data.get_one_of_inputs = MagicMock(
            side_effect=lambda x, default=None: {
                "biz_cc_id": 2,
                "cc_host_ip": "1.1.1.1",
                "cc_module_select": ["module_1"],
                "cc_is_increment": "true",
            }.get(x, default)
        )

        mock_client = MagicMock()
        mock_client.api.transfer_host_module = MagicMock(return_value={"result": False, "message": "api fail"})
        mock_get_client.return_value = mock_client

        mock_handle_error.return_value = "formatted error"

        with patch.object(self.service, "get_ip_info_list") as mock_get_ip_info:
            mock_get_ip_info.return_value = {"result": True, "ip_result": [{"HostID": 100}]}

            result = self.service.execute(data, parent_data)

        self.assertFalse(result)
        data.set_outputs.assert_called_with("ex_data", "formatted error")

    @patch("pipeline_plugins.components.collections.sites.open.cc.transfer_host_module.legacy.get_client_by_username")
    def test_execute_is_increment_false(self, mock_get_client):
        parent_data = MagicMock()
        parent_data.get_one_of_inputs = MagicMock(
            side_effect=lambda x, default=None: {
                "executor": "admin",
                "tenant_id": "system",
            }.get(x, default)
        )
        parent_data.inputs.biz_cc_id = 2

        data = MagicMock()
        data.get_one_of_inputs = MagicMock(
            side_effect=lambda x, default=None: {
                "biz_cc_id": 2,
                "cc_host_ip": "1.1.1.1",
                "cc_module_select": ["module_1"],
                "cc_is_increment": "false",
            }.get(x, default)
        )

        mock_client = MagicMock()
        mock_client.api.transfer_host_module = MagicMock(return_value={"result": True})
        mock_get_client.return_value = mock_client

        with patch.object(self.service, "get_ip_info_list") as mock_get_ip_info:
            mock_get_ip_info.return_value = {"result": True, "ip_result": [{"HostID": 100}]}

            result = self.service.execute(data, parent_data)

        self.assertTrue(result)
        call_args = mock_client.api.transfer_host_module.call_args[0][0]
        self.assertEqual(call_args["is_increment"], False)


class CCTransferHostModuleComponentTestCase(TestCase):
    def test_component(self):
        self.assertEqual(CCTransferHostModuleComponent.code, "cc_transfer_host_module")
        self.assertEqual(CCTransferHostModuleComponent.bound_service, CCTransferHostModuleService)
