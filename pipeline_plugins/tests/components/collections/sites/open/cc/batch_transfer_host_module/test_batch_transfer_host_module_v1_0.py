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

import unittest.mock

from django.test import TestCase
from mock import MagicMock, patch

from pipeline_plugins.components.collections.sites.open.cc.batch_transfer_host_module.v1_0 import (
    CCBatchTransferHostModule,
    CCBatchTransferHostModuleComponent,
)


class CCBatchTransferHostModuleTestCase(TestCase):
    def setUp(self):
        self.service = CCBatchTransferHostModule()
        self.service.logger = MagicMock()

    def test_inputs_format(self):
        inputs = self.service.inputs_format()
        self.assertEqual(len(inputs), 4)
        self.assertEqual(inputs[0].key, "cc_transfer_select_method_method")
        self.assertEqual(inputs[1].key, "cc_host_transfer_detail")
        self.assertEqual(inputs[2].key, "cc_transfer_host_template_break_line")
        self.assertEqual(inputs[3].key, "is_append")

    def test_outputs_format(self):
        outputs = self.service.outputs_format()
        self.assertEqual(len(outputs), 2)
        self.assertEqual(outputs[0].key, "set_update_success")
        self.assertEqual(outputs[1].key, "set_update_failed")

    @patch(
        "pipeline_plugins.components.collections.sites.open.cc.batch_transfer_host_module.v1_0."
        "get_client_by_username"
    )
    @patch(
        "pipeline_plugins.components.collections.sites.open.cc.batch_transfer_host_module.v1_0."
        "cc_list_select_node_inst_id"
    )
    def test_execute_manual_mode_success(self, mock_cc_list_select, mock_get_client):
        # 准备mock数据
        parent_data = MagicMock()
        parent_data.get_one_of_inputs = MagicMock(
            side_effect=lambda x, default=None: {
                "executor": "admin",
                "tenant_id": "system",
                "biz_cc_id": 2,
                "bk_biz_name": "test_biz",
            }.get(x, default)
        )
        parent_data.inputs.biz_cc_id = 2

        data = MagicMock()
        data.get_one_of_inputs = MagicMock(
            side_effect=lambda x, default=None: {
                "biz_cc_id": 2,
                "cc_module_select_method": "manual",
                "cc_host_transfer_detail": [
                    {"cc_transfer_host_ip": "192.168.1.1", "cc_transfer_host_target_module": "set1>module1"}
                ],
                "cc_transfer_host_template_break_line": ",",
                "is_append": True,
            }.get(x, default)
        )

        # mock client
        mock_client = MagicMock()
        mock_client.api.transfer_host_module = MagicMock(return_value={"result": True})
        mock_get_client.return_value = mock_client

        # mock 其他函数
        mock_cc_list_select.return_value = {"result": True, "data": [10]}

        # mock get_host_list
        with patch.object(self.service, "get_host_list", return_value={"result": True, "data": ["100"]}):
            # 执行
            result = self.service.execute(data, parent_data)

        # 断言
        self.assertTrue(result)
        data.set_outputs.assert_any_call("transfer_host_module_success", unittest.mock.ANY)

    @patch(
        "pipeline_plugins.components.collections.sites.open.cc.batch_transfer_host_module.v1_0.get_client_by_username"
    )
    @patch("pipeline_plugins.components.collections.sites.open.cc.batch_transfer_host_module.v1_0.chunk_table_data")
    def test_execute_auto_mode_chunk_fail(self, mock_chunk_table_data, mock_get_client):
        parent_data = MagicMock()
        parent_data.get_one_of_inputs = MagicMock(
            side_effect=lambda x, default=None: {
                "executor": "admin",
                "tenant_id": "system",
                "biz_cc_id": 2,
                "bk_biz_name": "test_biz",
            }.get(x, default)
        )
        parent_data.inputs.biz_cc_id = 2

        data = MagicMock()
        data.get_one_of_inputs = MagicMock(
            side_effect=lambda x, default=None: {
                "biz_cc_id": 2,
                "cc_module_select_method": "auto",
                "cc_host_transfer_detail": [{"field": "value1,value2"}],
                "cc_transfer_host_template_break_line": ",",
                "is_append": True,
            }.get(x, default)
        )

        # mock chunk_table_data 返回失败
        mock_chunk_table_data.return_value = {"result": False, "message": "chunk failed"}

        # 执行
        result = self.service.execute(data, parent_data)

        # 断言
        self.assertFalse(result)
        data.set_outputs.assert_called_with("ex_data", "chunk failed")

    @patch(
        "pipeline_plugins.components.collections.sites.open.cc.batch_transfer_host_module.v1_0.get_client_by_username"
    )
    def test_execute_get_host_list_fail(self, mock_get_client):
        parent_data = MagicMock()
        parent_data.get_one_of_inputs = MagicMock(
            side_effect=lambda x, default=None: {
                "executor": "admin",
                "tenant_id": "system",
                "biz_cc_id": 2,
                "bk_biz_name": "test_biz",
            }.get(x, default)
        )
        parent_data.inputs.biz_cc_id = 2

        data = MagicMock()
        data.get_one_of_inputs = MagicMock(
            side_effect=lambda x, default=None: {
                "biz_cc_id": 2,
                "cc_module_select_method": "manual",
                "cc_host_transfer_detail": [
                    {"cc_transfer_host_ip": "192.168.1.1", "cc_transfer_host_target_module": "set1>module1"}
                ],
                "cc_transfer_host_template_break_line": ",",
                "is_append": True,
            }.get(x, default)
        )

        # mock get_host_list 返回失败
        with patch.object(self.service, "get_host_list", return_value={"result": False, "message": "host not found"}):
            # 执行
            result = self.service.execute(data, parent_data)

        # 断言
        self.assertFalse(result)
        data.set_outputs.assert_any_call("ex_data", unittest.mock.ANY)

    @patch(
        "pipeline_plugins.components.collections.sites.open.cc.batch_transfer_host_module.v1_0.get_client_by_username"
    )
    @patch(
        "pipeline_plugins.components.collections.sites.open.cc.batch_transfer_host_module.v1_0."
        "cc_list_select_node_inst_id"
    )
    def test_execute_cc_list_select_node_inst_id_fail(self, mock_cc_list_select, mock_get_client):
        parent_data = MagicMock()
        parent_data.get_one_of_inputs = MagicMock(
            side_effect=lambda x, default=None: {
                "executor": "admin",
                "tenant_id": "system",
                "biz_cc_id": 2,
                "bk_biz_name": "test_biz",
            }.get(x, default)
        )
        parent_data.inputs.biz_cc_id = 2

        data = MagicMock()
        data.get_one_of_inputs = MagicMock(
            side_effect=lambda x, default=None: {
                "biz_cc_id": 2,
                "cc_module_select_method": "manual",
                "cc_host_transfer_detail": [
                    {"cc_transfer_host_ip": "192.168.1.1", "cc_transfer_host_target_module": "set1>module1"}
                ],
                "cc_transfer_host_template_break_line": ",",
                "is_append": True,
            }.get(x, default)
        )

        # mock cc_list_select_node_inst_id 返回失败
        mock_cc_list_select.return_value = {"result": False, "message": "node not found"}

        # mock get_host_list
        with patch.object(self.service, "get_host_list", return_value={"result": True, "data": ["100"]}):
            # 执行
            result = self.service.execute(data, parent_data)

        # 断言
        self.assertFalse(result)
        data.set_outputs.assert_any_call("ex_data", unittest.mock.ANY)

    @patch(
        "pipeline_plugins.components.collections.sites.open.cc.batch_transfer_host_module.v1_0.get_client_by_username"
    )
    @patch(
        "pipeline_plugins.components.collections.sites.open.cc.batch_transfer_host_module.v1_0."
        "cc_list_select_node_inst_id"
    )
    def test_execute_transfer_host_module_fail(self, mock_cc_list_select, mock_get_client):
        parent_data = MagicMock()
        parent_data.get_one_of_inputs = MagicMock(
            side_effect=lambda x, default=None: {
                "executor": "admin",
                "tenant_id": "system",
                "biz_cc_id": 2,
                "bk_biz_name": "test_biz",
            }.get(x, default)
        )
        parent_data.inputs.biz_cc_id = 2

        data = MagicMock()
        data.get_one_of_inputs = MagicMock(
            side_effect=lambda x, default=None: {
                "biz_cc_id": 2,
                "cc_module_select_method": "manual",
                "cc_host_transfer_detail": [
                    {"cc_transfer_host_ip": "192.168.1.1", "cc_transfer_host_target_module": "set1>module1"}
                ],
                "cc_transfer_host_template_break_line": ",",
                "is_append": True,
            }.get(x, default)
        )

        # mock client
        mock_client = MagicMock()
        mock_client.api.transfer_host_module = MagicMock(return_value={"result": False, "message": "transfer failed"})
        mock_get_client.return_value = mock_client

        # mock 其他函数
        mock_cc_list_select.return_value = {"result": True, "data": [10]}

        # mock get_host_list
        with patch.object(self.service, "get_host_list", return_value={"result": True, "data": ["100"]}):
            # 执行
            result = self.service.execute(data, parent_data)

        # 断言
        self.assertFalse(result)
        data.set_outputs.assert_any_call("ex_data", unittest.mock.ANY)

    @patch(
        "pipeline_plugins.components.collections.sites.open.cc.batch_transfer_host_module.v1_0.get_client_by_username"
    )
    @patch(
        "pipeline_plugins.components.collections.sites.open.cc.batch_transfer_host_module.v1_0."
        "cc_list_select_node_inst_id"
    )
    def test_execute_with_is_append_false(self, mock_cc_list_select, mock_get_client):
        # 测试 is_append=False 的情况
        parent_data = MagicMock()
        parent_data.get_one_of_inputs = MagicMock(
            side_effect=lambda x, default=None: {
                "executor": "admin",
                "tenant_id": "system",
                "biz_cc_id": 2,
                "bk_biz_name": "test_biz",
            }.get(x, default)
        )
        parent_data.inputs.biz_cc_id = 2

        data = MagicMock()
        data.get_one_of_inputs = MagicMock(
            side_effect=lambda x, default=None: {
                "biz_cc_id": 2,
                "cc_module_select_method": "manual",
                "cc_host_transfer_detail": [
                    {"cc_transfer_host_ip": "192.168.1.1", "cc_transfer_host_target_module": "set1>module1"}
                ],
                "cc_transfer_host_template_break_line": ",",
                "is_append": False,
            }.get(x, default)
        )

        # mock client
        mock_client = MagicMock()
        mock_client.api.transfer_host_module = MagicMock(return_value={"result": True})
        mock_get_client.return_value = mock_client

        # mock 其他函数
        mock_cc_list_select.return_value = {"result": True, "data": [10]}

        # mock get_host_list
        with patch.object(self.service, "get_host_list", return_value={"result": True, "data": ["100"]}):
            # 执行
            result = self.service.execute(data, parent_data)

        # 断言
        self.assertTrue(result)
        # 验证 is_increment=False 被传递
        call_args = mock_client.api.transfer_host_module.call_args
        self.assertEqual(call_args[0][0]["is_increment"], False)


class CCBatchTransferHostModuleComponentTestCase(TestCase):
    def test_component_code(self):
        component = CCBatchTransferHostModuleComponent
        self.assertEqual(component.code, "cc_batch_transfer_host_module")
        self.assertEqual(component.bound_service, CCBatchTransferHostModule)
