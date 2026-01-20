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

from pipeline_plugins.components.collections.sites.open.cc.batch_module_update.v1_0 import (
    CCBatchModuleUpdateComponent,
    CCBatchModuleUpdateService,
)


class CCBatchModuleUpdateServiceTestCase(TestCase):
    def setUp(self):
        self.service = CCBatchModuleUpdateService()
        self.service.logger = MagicMock()

    def test_inputs_format(self):
        inputs = self.service.inputs_format()
        self.assertEqual(len(inputs), 3)
        self.assertEqual(inputs[0].key, "cc_tag_method")
        self.assertEqual(inputs[1].key, "cc_module_update_data")
        self.assertEqual(inputs[2].key, "cc_template_break_line")

    def test_outputs_format(self):
        outputs = self.service.outputs_format()
        self.assertEqual(len(outputs), 2)
        self.assertEqual(outputs[0].key, "module_update_success")
        self.assertEqual(outputs[1].key, "module_update_failed")

    @patch("pipeline_plugins.components.collections.sites.open.cc.batch_module_update.v1_0.get_client_by_username")
    @patch("pipeline_plugins.components.collections.sites.open.cc.batch_module_update.v1_0.cc_list_select_node_inst_id")
    @patch("pipeline_plugins.components.collections.sites.open.cc.batch_module_update.v1_0.get_module_set_id")
    def test_execute_manual_mode_success(self, mock_get_module_set_id, mock_cc_list_select, mock_get_client):
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
        parent_data.inputs.bk_biz_name = "test_biz"

        data = MagicMock()
        data.get_one_of_inputs = MagicMock(
            side_effect=lambda x, default=None: {
                "biz_cc_id": 2,
                "cc_tag_method": "manual",
                "cc_module_update_data": [
                    {"cc_module_select_text": "set1>module1", "bk_module_name": "new_module_name"}
                ],
                "cc_template_break_line": ",",
            }.get(x, default)
        )

        # mock client
        mock_client = MagicMock()
        mock_client.api.search_biz_inst_topo = MagicMock(
            return_value={
                "result": True,
                "data": [
                    {
                        "bk_inst_id": 1,
                        "bk_inst_name": "set1",
                        "bk_obj_id": "set",
                        "child": [{"bk_inst_id": 10, "bk_inst_name": "module1", "bk_obj_id": "module"}],
                    }
                ],
            }
        )
        mock_client.api.search_object_attribute = MagicMock(
            return_value={
                "result": True,
                "data": [{"bk_property_id": "bk_module_name", "bk_property_type": "singlechar"}],
            }
        )
        mock_client.api.update_module = MagicMock(return_value={"result": True})
        mock_get_client.return_value = mock_client

        # mock 其他函数
        mock_cc_list_select.return_value = {"result": True, "data": [10]}
        mock_get_module_set_id.return_value = 1

        # 执行
        result = self.service.execute(data, parent_data)

        # 断言
        self.assertTrue(result)
        data.set_outputs.assert_any_call(
            "module_update_success", [{"cc_module_select_text": "set1>module1", "bk_module_name": "new_module_name"}]
        )

    @patch("pipeline_plugins.components.collections.sites.open.cc.batch_module_update.v1_0.get_client_by_username")
    def test_execute_search_biz_inst_topo_fail(self, mock_get_client):
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
        parent_data.inputs.bk_biz_name = "test_biz"

        data = MagicMock()
        data.get_one_of_inputs = MagicMock(
            side_effect=lambda x, default=None: {
                "biz_cc_id": 2,
                "cc_tag_method": "manual",
                "cc_module_update_data": [],
                "cc_template_break_line": ",",
            }.get(x, default)
        )

        # mock client 返回失败
        mock_client = MagicMock()
        mock_client.api.search_biz_inst_topo = MagicMock(return_value={"result": False, "message": "search failed"})
        mock_get_client.return_value = mock_client

        # 执行
        result = self.service.execute(data, parent_data)

        # 断言
        self.assertFalse(result)
        data.set_outputs.assert_called_with("ex_data", unittest.mock.ANY)

    @patch("pipeline_plugins.components.collections.sites.open.cc.batch_module_update.v1_0.get_client_by_username")
    def test_execute_search_object_attribute_fail(self, mock_get_client):
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
        parent_data.inputs.bk_biz_name = "test_biz"

        data = MagicMock()
        data.get_one_of_inputs = MagicMock(
            side_effect=lambda x, default=None: {
                "biz_cc_id": 2,
                "cc_tag_method": "manual",
                "cc_module_update_data": [],
                "cc_template_break_line": ",",
            }.get(x, default)
        )

        # mock client
        mock_client = MagicMock()
        mock_client.api.search_biz_inst_topo = MagicMock(return_value={"result": True, "data": []})
        mock_client.api.search_object_attribute = MagicMock(
            return_value={"result": False, "message": "attribute search failed"}
        )
        mock_get_client.return_value = mock_client

        # 执行
        result = self.service.execute(data, parent_data)

        # 断言
        self.assertFalse(result)
        data.set_outputs.assert_called_with("ex_data", unittest.mock.ANY)

    @patch("pipeline_plugins.components.collections.sites.open.cc.batch_module_update.v1_0.get_client_by_username")
    @patch("pipeline_plugins.components.collections.sites.open.cc.batch_module_update.v1_0.chunk_table_data")
    def test_execute_template_mode_chunk_fail(self, mock_chunk_table_data, mock_get_client):
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
        parent_data.inputs.bk_biz_name = "test_biz"

        data = MagicMock()
        data.get_one_of_inputs = MagicMock(
            side_effect=lambda x, default=None: {
                "biz_cc_id": 2,
                "cc_tag_method": "template",
                "cc_module_update_data": [{"field": "value1,value2"}],
                "cc_template_break_line": ",",
            }.get(x, default)
        )

        # mock chunk_table_data 返回失败
        mock_chunk_table_data.return_value = {"result": False, "message": "chunk failed"}

        # 执行
        result = self.service.execute(data, parent_data)

        # 断言
        self.assertFalse(result)
        data.set_outputs.assert_called_with("ex_data", "chunk failed")

    @patch("pipeline_plugins.components.collections.sites.open.cc.batch_module_update.v1_0.get_client_by_username")
    @patch("pipeline_plugins.components.collections.sites.open.cc.batch_module_update.v1_0.cc_list_select_node_inst_id")
    @patch("pipeline_plugins.components.collections.sites.open.cc.batch_module_update.v1_0.get_module_set_id")
    def test_execute_attribute_type_transform_fail(self, mock_get_module_set_id, mock_cc_list_select, mock_get_client):
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
        parent_data.inputs.bk_biz_name = "test_biz"

        data = MagicMock()
        data.get_one_of_inputs = MagicMock(
            side_effect=lambda x, default=None: {
                "biz_cc_id": 2,
                "cc_tag_method": "manual",
                "cc_module_update_data": [{"cc_module_select_text": "set1>module1", "bk_module_type": "invalid_int"}],
                "cc_template_break_line": ",",
            }.get(x, default)
        )

        # mock client
        mock_client = MagicMock()
        mock_client.api.search_biz_inst_topo = MagicMock(return_value={"result": True, "data": []})
        mock_client.api.search_object_attribute = MagicMock(
            return_value={
                "result": True,
                "data": [{"bk_property_id": "bk_module_type", "bk_property_type": "int"}],
            }
        )
        mock_get_client.return_value = mock_client

        # 执行
        result = self.service.execute(data, parent_data)

        # 断言
        self.assertFalse(result)
        data.set_outputs.assert_any_call("module_update_failed", unittest.mock.ANY)

    @patch("pipeline_plugins.components.collections.sites.open.cc.batch_module_update.v1_0.get_client_by_username")
    @patch("pipeline_plugins.components.collections.sites.open.cc.batch_module_update.v1_0.cc_list_select_node_inst_id")
    @patch("pipeline_plugins.components.collections.sites.open.cc.batch_module_update.v1_0.get_module_set_id")
    def test_execute_missing_module_text(self, mock_get_module_set_id, mock_cc_list_select, mock_get_client):
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
        parent_data.inputs.bk_biz_name = "test_biz"

        data = MagicMock()
        data.get_one_of_inputs = MagicMock(
            side_effect=lambda x, default=None: {
                "biz_cc_id": 2,
                "cc_tag_method": "manual",
                "cc_module_update_data": [{"bk_module_name": "new_name"}],  # 缺少 cc_module_select_text
                "cc_template_break_line": ",",
            }.get(x, default)
        )

        # mock client
        mock_client = MagicMock()
        mock_client.api.search_biz_inst_topo = MagicMock(return_value={"result": True, "data": []})
        mock_client.api.search_object_attribute = MagicMock(return_value={"result": True, "data": []})
        mock_get_client.return_value = mock_client

        # 执行
        result = self.service.execute(data, parent_data)

        # 断言
        self.assertFalse(result)
        data.set_outputs.assert_any_call("module_update_failed", unittest.mock.ANY)

    @patch("pipeline_plugins.components.collections.sites.open.cc.batch_module_update.v1_0.get_client_by_username")
    @patch("pipeline_plugins.components.collections.sites.open.cc.batch_module_update.v1_0.cc_list_select_node_inst_id")
    @patch("pipeline_plugins.components.collections.sites.open.cc.batch_module_update.v1_0.get_module_set_id")
    def test_execute_cc_list_select_node_inst_id_fail(
        self, mock_get_module_set_id, mock_cc_list_select, mock_get_client
    ):
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
        parent_data.inputs.bk_biz_name = "test_biz"

        data = MagicMock()
        data.get_one_of_inputs = MagicMock(
            side_effect=lambda x, default=None: {
                "biz_cc_id": 2,
                "cc_tag_method": "manual",
                "cc_module_update_data": [{"cc_module_select_text": "set1>module1", "bk_module_name": "new_name"}],
                "cc_template_break_line": ",",
            }.get(x, default)
        )

        # mock client
        mock_client = MagicMock()
        mock_client.api.search_biz_inst_topo = MagicMock(return_value={"result": True, "data": []})
        mock_client.api.search_object_attribute = MagicMock(return_value={"result": True, "data": []})
        mock_get_client.return_value = mock_client

        # mock cc_list_select_node_inst_id 返回失败
        mock_cc_list_select.return_value = {"result": False, "message": "node not found"}

        # 执行
        result = self.service.execute(data, parent_data)

        # 断言
        self.assertFalse(result)
        data.set_outputs.assert_any_call("module_update_failed", unittest.mock.ANY)

    @patch("pipeline_plugins.components.collections.sites.open.cc.batch_module_update.v1_0.get_client_by_username")
    @patch("pipeline_plugins.components.collections.sites.open.cc.batch_module_update.v1_0.cc_list_select_node_inst_id")
    @patch("pipeline_plugins.components.collections.sites.open.cc.batch_module_update.v1_0.get_module_set_id")
    def test_execute_update_module_fail(self, mock_get_module_set_id, mock_cc_list_select, mock_get_client):
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
        parent_data.inputs.bk_biz_name = "test_biz"

        data = MagicMock()
        data.get_one_of_inputs = MagicMock(
            side_effect=lambda x, default=None: {
                "biz_cc_id": 2,
                "cc_tag_method": "manual",
                "cc_module_update_data": [{"cc_module_select_text": "set1>module1", "bk_module_name": "new_name"}],
                "cc_template_break_line": ",",
            }.get(x, default)
        )

        # mock client
        mock_client = MagicMock()
        mock_client.api.search_biz_inst_topo = MagicMock(return_value={"result": True, "data": []})
        mock_client.api.search_object_attribute = MagicMock(return_value={"result": True, "data": []})
        mock_client.api.update_module = MagicMock(return_value={"result": False, "message": "update failed"})
        mock_get_client.return_value = mock_client

        # mock 其他函数
        mock_cc_list_select.return_value = {"result": True, "data": [10]}
        mock_get_module_set_id.return_value = 1

        # 执行
        result = self.service.execute(data, parent_data)

        # 断言
        self.assertFalse(result)
        data.set_outputs.assert_any_call("module_update_failed", unittest.mock.ANY)


class CCBatchModuleUpdateComponentTestCase(TestCase):
    def setUp(self):
        self.component = CCBatchModuleUpdateComponent

    def test_component_code(self):
        self.assertEqual(self.component.code, "cc_batch_module_update")
        self.assertEqual(self.component.bound_service, CCBatchModuleUpdateService)
