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

from pipeline_plugins.components.collections.sites.open.cc.base import BaseTransferHostToModuleService


class MockTransferService(BaseTransferHostToModuleService):
    """Mock implementation for testing"""

    def execute(self, data, parent_data):
        """Mock execute method"""
        pass


class BaseTransferHostToModuleServiceTestCase(TestCase):
    def setUp(self):
        self.service = MockTransferService()
        self.data = MagicMock()
        self.parent_data = MagicMock()
        self.transfer_cmd = "transfer_host_to_faultmodule"

        # Setup mock inputs
        self.parent_data.get_one_of_inputs = MagicMock(
            side_effect=lambda key, default=None: {
                "executor": "admin",
                "tenant_id": "system",
                "language": "zh-cn",
            }.get(key, default)
        )

        self.data.get_one_of_inputs = MagicMock(
            side_effect=lambda key, default=None: {"biz_cc_id": 2, "cc_host_ip": "1.1.1.1,2.2.2.2"}.get(key, default)
        )

        self.parent_data.inputs.biz_cc_id = 2

    def test__inputs_format(self):
        inputs = self.service.inputs_format()
        self.assertEqual(len(inputs), 2)
        self.assertEqual(inputs[0].key, "biz_cc_id")
        self.assertEqual(inputs[1].key, "cc_host_ip")

    def test__outputs_format(self):
        outputs = self.service.outputs_format()
        self.assertEqual(outputs, [])

    @patch("pipeline_plugins.components.collections.sites.open.cc.base.get_client_by_username")
    def test__exec_transfer_host_module_get_host_fail(self, mock_get_client):
        self.service.get_host_list = MagicMock(return_value={"result": False, "message": "host not found"})

        result = self.service.exec_transfer_host_module(self.data, self.parent_data, self.transfer_cmd)

        self.assertFalse(result)
        self.data.set_outputs.assert_called_once_with("ex_data", "host not found")

    @patch("pipeline_plugins.components.collections.sites.open.cc.base.get_client_by_username")
    def test__exec_transfer_host_module_transfer_fail(self, mock_get_client):
        mock_client = MagicMock()
        mock_api_method = MagicMock(return_value={"result": False, "message": "transfer failed"})
        setattr(mock_client.api, self.transfer_cmd, mock_api_method)
        mock_get_client.return_value = mock_client

        self.service.get_host_list = MagicMock(return_value={"result": True, "data": ["1", "2", "3"]})
        self.service.logger = MagicMock()

        result = self.service.exec_transfer_host_module(self.data, self.parent_data, self.transfer_cmd)

        self.assertFalse(result)
        self.service.logger.error.assert_called_once()
        self.data.set_outputs.assert_called_once()
        call_args = self.data.set_outputs.call_args[0]
        self.assertEqual(call_args[0], "ex_data")
        self.assertIn("transfer failed", call_args[1])

    @patch("pipeline_plugins.components.collections.sites.open.cc.base.get_client_by_username")
    def test__exec_transfer_host_module_success(self, mock_get_client):
        mock_client = MagicMock()
        mock_api_method = MagicMock(return_value={"result": True})
        setattr(mock_client.api, self.transfer_cmd, mock_api_method)
        mock_get_client.return_value = mock_client

        self.service.get_host_list = MagicMock(return_value={"result": True, "data": ["1", "2", "3"]})

        result = self.service.exec_transfer_host_module(self.data, self.parent_data, self.transfer_cmd)

        self.assertTrue(result)
        mock_api_method.assert_called_once()
        call_kwargs = mock_api_method.call_args[0][0]
        self.assertEqual(call_kwargs["bk_biz_id"], 2)
        self.assertEqual(call_kwargs["bk_host_id"], [1, 2, 3])

    @patch("pipeline_plugins.components.collections.sites.open.cc.base.translation")
    @patch("pipeline_plugins.components.collections.sites.open.cc.base.get_client_by_username")
    def test__exec_transfer_host_module_with_language(self, mock_get_client, mock_translation):
        mock_client = MagicMock()
        mock_api_method = MagicMock(return_value={"result": True})
        setattr(mock_client.api, self.transfer_cmd, mock_api_method)
        mock_get_client.return_value = mock_client

        self.service.get_host_list = MagicMock(return_value={"result": True, "data": ["1"]})

        result = self.service.exec_transfer_host_module(self.data, self.parent_data, self.transfer_cmd)

        self.assertTrue(result)
        mock_translation.activate.assert_called_once_with("zh-cn")
        self.assertEqual(mock_client.language, "zh-cn")

    @patch("pipeline_plugins.components.collections.sites.open.cc.base.get_client_by_username")
    def test__exec_transfer_host_module_no_language(self, mock_get_client):
        # Test when language is not provided
        self.parent_data.get_one_of_inputs = MagicMock(
            side_effect=lambda key, default=None: {
                "executor": "admin",
                "tenant_id": "system",
                "language": None,
            }.get(key, default)
        )

        mock_client = MagicMock()
        mock_api_method = MagicMock(return_value={"result": True})
        setattr(mock_client.api, self.transfer_cmd, mock_api_method)
        mock_get_client.return_value = mock_client

        self.service.get_host_list = MagicMock(return_value={"result": True, "data": ["1"]})

        result = self.service.exec_transfer_host_module(self.data, self.parent_data, self.transfer_cmd)

        self.assertTrue(result)
