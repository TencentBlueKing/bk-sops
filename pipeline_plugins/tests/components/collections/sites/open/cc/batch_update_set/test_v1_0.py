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
from mock import ANY, MagicMock, patch

from pipeline_plugins.components.collections.sites.open.cc.batch_update_set.v1_0 import CCBatchUpdateSetService


class CCBatchUpdateSetServiceTestCase(TestCase):
    def setUp(self):
        self.service = CCBatchUpdateSetService()
        self.service.logger = MagicMock()

    @patch("pipeline_plugins.components.collections.sites.open.cc.batch_update_set.v1_0.get_client_by_username")
    @patch(
        "pipeline_plugins.components.collections.sites.open.cc.batch_update_set.v1_0."
        "EnvironmentVariables.objects.get_var"
    )
    def test_execute_success(self, _, mock_get_client):
        # Mock inputs
        executor = "admin"
        tenant_id = "1"
        biz_cc_id = "2"
        cc_set_select_method = "manual"
        cc_set_update_data = [
            {"bk_set_name": "set1", "bk_capacity": "100"},
            {"bk_set_name": "set2", "bk_capacity": "200"},
        ]

        data = MagicMock()
        data.get_one_of_inputs.side_effect = lambda key, default=None: {
            "biz_cc_id": biz_cc_id,
            "cc_set_select_method": cc_set_select_method,
            "cc_set_update_data": cc_set_update_data,
            "cc_set_template_break_line": ",",
        }.get(key, default)

        parent_data = MagicMock()
        parent_data.get_one_of_inputs.side_effect = lambda key: {
            "executor": executor,
            "tenant_id": tenant_id,
        }.get(key)
        parent_data.inputs.biz_cc_id = biz_cc_id

        # Mock client
        client = MagicMock()
        mock_get_client.return_value = client

        # Mock search_object_attribute
        client.api.search_object_attribute.return_value = {
            "result": True,
            "data": [
                {"bk_property_id": "bk_capacity", "bk_property_type": "int"},
                {"bk_property_id": "bk_set_name", "bk_property_type": "singlechar"},
            ],
        }

        # Mock search_set
        client.api.search_set.side_effect = [
            {"result": True, "data": {"info": [{"bk_set_name": "set1", "bk_set_id": 101}]}},
            {"result": True, "data": {"info": [{"bk_set_name": "set2", "bk_set_id": 102}]}},
        ]

        # Mock update_set
        client.api.update_set.return_value = {"result": True}

        # Execute
        result = self.service.execute(data, parent_data)

        # Assertions
        self.assertTrue(result)

        # Verify update_set calls
        self.assertEqual(client.api.update_set.call_count, 2)

        # Verify outputs
        expected_success = [
            {"bk_set_name": "set1", "bk_capacity": "100"},
            {"bk_set_name": "set2", "bk_capacity": "200"},
        ]
        calls = data.set_outputs.call_args_list
        success_call = [c for c in calls if c[0][0] == "set_update_success"]
        self.assertTrue(success_call)
        self.assertEqual(success_call[0][0][1], expected_success)

        data.set_outputs.assert_any_call("set_update_failed", [])

    @patch("pipeline_plugins.components.collections.sites.open.cc.batch_update_set.v1_0.get_client_by_username")
    @patch(
        "pipeline_plugins.components.collections.sites.open.cc.batch_update_set.v1_0."
        "EnvironmentVariables.objects.get_var"
    )
    @patch("pipeline_plugins.components.collections.sites.open.cc.batch_update_set.v1_0.chunk_table_data")
    def test_execute_auto_success(self, mock_chunk_table_data, _, mock_get_client):
        # Mock inputs
        executor = "admin"
        tenant_id = "1"
        biz_cc_id = "2"
        cc_set_select_method = "auto"
        cc_set_update_data = [{"bk_set_name": "set1,set2", "bk_capacity": "100,200"}]

        data = MagicMock()
        data.get_one_of_inputs.side_effect = lambda key, default=None: {
            "biz_cc_id": biz_cc_id,
            "cc_set_select_method": cc_set_select_method,
            "cc_set_update_data": cc_set_update_data,
            "cc_set_template_break_line": ",",
        }.get(key, default)

        parent_data = MagicMock()
        parent_data.get_one_of_inputs.side_effect = lambda key: {
            "executor": executor,
            "tenant_id": tenant_id,
        }.get(key)
        parent_data.inputs.biz_cc_id = biz_cc_id

        # Mock chunk_table_data
        mock_chunk_table_data.return_value = {
            "result": True,
            "data": [{"bk_set_name": "set1", "bk_capacity": "100"}, {"bk_set_name": "set2", "bk_capacity": "200"}],
        }

        # Mock client
        client = MagicMock()
        mock_get_client.return_value = client

        # Mock search_object_attribute
        client.api.search_object_attribute.return_value = {
            "result": True,
            "data": [
                {"bk_property_id": "bk_capacity", "bk_property_type": "int"},
                {"bk_property_id": "bk_set_name", "bk_property_type": "singlechar"},
            ],
        }

        # Mock search_set
        client.api.search_set.side_effect = [
            {"result": True, "data": {"info": [{"bk_set_name": "set1", "bk_set_id": 101}]}},
            {"result": True, "data": {"info": [{"bk_set_name": "set2", "bk_set_id": 102}]}},
        ]

        # Mock update_set
        client.api.update_set.return_value = {"result": True}

        # Execute
        result = self.service.execute(data, parent_data)

        # Assertions
        self.assertTrue(result)
        self.assertEqual(client.api.update_set.call_count, 2)

    @patch("pipeline_plugins.components.collections.sites.open.cc.batch_update_set.v1_0.get_client_by_username")
    @patch(
        "pipeline_plugins.components.collections.sites.open.cc.batch_update_set.v1_0."
        "EnvironmentVariables.objects.get_var"
    )
    def test_execute_search_attr_fail(self, _, mock_get_client):
        # Mock inputs
        executor = "admin"
        tenant_id = "1"
        biz_cc_id = "2"
        cc_set_select_method = "manual"
        cc_set_update_data = []

        data = MagicMock()
        data.get_one_of_inputs.side_effect = lambda key, default=None: {
            "biz_cc_id": biz_cc_id,
            "cc_set_select_method": cc_set_select_method,
            "cc_set_update_data": cc_set_update_data,
            "cc_set_template_break_line": ",",
        }.get(key, default)

        parent_data = MagicMock()
        parent_data.get_one_of_inputs.side_effect = lambda key: {
            "executor": executor,
            "tenant_id": tenant_id,
        }.get(key)
        parent_data.inputs.biz_cc_id = biz_cc_id

        # Mock client
        client = MagicMock()
        mock_get_client.return_value = client

        # Mock search_object_attribute fail
        client.api.search_object_attribute.return_value = {"result": False, "message": "search attr failed"}

        # Execute
        result = self.service.execute(data, parent_data)

        # Assertions
        self.assertFalse(result)
        # The actual message is formatted by handle_api_error
        data.set_outputs.assert_called()
        args, _ = data.set_outputs.call_args
        self.assertEqual(args[0], "ex_data")
        self.assertIn("search attr failed", args[1])

    @patch("pipeline_plugins.components.collections.sites.open.cc.batch_update_set.v1_0.get_client_by_username")
    @patch(
        "pipeline_plugins.components.collections.sites.open.cc.batch_update_set.v1_0."
        "EnvironmentVariables.objects.get_var"
    )
    def test_execute_update_fail(self, _, mock_get_client):
        # Mock inputs
        executor = "admin"
        tenant_id = "1"
        biz_cc_id = "2"
        cc_set_select_method = "manual"
        cc_set_update_data = [{"bk_set_name": "set1", "bk_capacity": "100"}]

        data = MagicMock()
        data.get_one_of_inputs.side_effect = lambda key, default=None: {
            "biz_cc_id": biz_cc_id,
            "cc_set_select_method": cc_set_select_method,
            "cc_set_update_data": cc_set_update_data,
            "cc_set_template_break_line": ",",
        }.get(key, default)

        parent_data = MagicMock()
        parent_data.get_one_of_inputs.side_effect = lambda key: {
            "executor": executor,
            "tenant_id": tenant_id,
        }.get(key)
        parent_data.inputs.biz_cc_id = biz_cc_id

        # Mock client
        client = MagicMock()
        mock_get_client.return_value = client

        # Mock search_object_attribute
        client.api.search_object_attribute.return_value = {
            "result": True,
            "data": [
                {"bk_property_id": "bk_capacity", "bk_property_type": "int"},
                {"bk_property_id": "bk_set_name", "bk_property_type": "singlechar"},
            ],
        }

        # Mock search_set
        client.api.search_set.return_value = {
            "result": True,
            "data": {"info": [{"bk_set_name": "set1", "bk_set_id": 101}]},
        }

        # Mock update_set fail
        client.api.update_set.return_value = {"result": False, "message": "update failed"}

        # Execute
        result = self.service.execute(data, parent_data)

        # Assertions
        # In test_execute_update_fail, we have failed updates, so it returns False
        self.assertFalse(result)

        # Verify outputs
        data.set_outputs.assert_any_call("set_update_success", [])
        # The last call is "ex_data" because failed_update is not empty and it returns False
        # But "set_update_failed" is also called before that.
        data.set_outputs.assert_any_call("set_update_failed", ANY)

        # Check ex_data
        args, _ = data.set_outputs.call_args_list[-1]
        self.assertEqual(args[0], "ex_data")
        self.assertIn("update failed", args[1][0])

    @patch("pipeline_plugins.components.collections.sites.open.cc.batch_update_set.v1_0.get_client_by_username")
    @patch(
        "pipeline_plugins.components.collections.sites.open.cc.batch_update_set.v1_0."
        "EnvironmentVariables.objects.get_var"
    )
    def test_execute_transform_fail(self, _, mock_get_client):
        # Mock inputs
        executor = "admin"
        tenant_id = "1"
        biz_cc_id = "2"
        cc_set_select_method = "manual"
        cc_set_update_data = [{"bk_set_name": "set1", "bk_capacity": "invalid_int"}]

        data = MagicMock()
        data.get_one_of_inputs.side_effect = lambda key, default=None: {
            "biz_cc_id": biz_cc_id,
            "cc_set_select_method": cc_set_select_method,
            "cc_set_update_data": cc_set_update_data,
            "cc_set_template_break_line": ",",
        }.get(key, default)

        parent_data = MagicMock()
        parent_data.get_one_of_inputs.side_effect = lambda key: {
            "executor": executor,
            "tenant_id": tenant_id,
        }.get(key)
        parent_data.inputs.biz_cc_id = biz_cc_id

        # Mock client
        client = MagicMock()
        mock_get_client.return_value = client

        # Mock search_object_attribute
        client.api.search_object_attribute.return_value = {
            "result": True,
            "data": [
                {"bk_property_id": "bk_capacity", "bk_property_type": "int"},
                {"bk_property_id": "bk_set_name", "bk_property_type": "singlechar"},
            ],
        }

        # Execute
        result = self.service.execute(data, parent_data)

        # Assertions
        self.assertFalse(result)

        # Verify outputs
        data.set_outputs.assert_any_call("set_update_success", [])
        data.set_outputs.assert_any_call("set_update_failed", ANY)

        args, _ = data.set_outputs.call_args_list[-1]
        self.assertEqual(args[0], "ex_data")
        self.assertIn("invalid_int", args[1][0])

    @patch("pipeline_plugins.components.collections.sites.open.cc.batch_update_set.v1_0.get_client_by_username")
    @patch(
        "pipeline_plugins.components.collections.sites.open.cc.batch_update_set.v1_0."
        "EnvironmentVariables.objects.get_var"
    )
    @patch("pipeline_plugins.components.collections.sites.open.cc.batch_update_set.v1_0.chunk_table_data")
    def test_execute_auto_chunk_fail(self, mock_chunk_table_data, _, mock_get_client):
        # Mock inputs
        executor = "admin"
        tenant_id = "1"
        biz_cc_id = "2"
        cc_set_select_method = "auto"
        cc_set_update_data = [{"bk_set_name": "set1,set2", "bk_capacity": "100"}]

        data = MagicMock()
        data.get_one_of_inputs.side_effect = lambda key, default=None: {
            "biz_cc_id": biz_cc_id,
            "cc_set_select_method": cc_set_select_method,
            "cc_set_update_data": cc_set_update_data,
            "cc_set_template_break_line": ",",
        }.get(key, default)

        parent_data = MagicMock()
        parent_data.get_one_of_inputs.side_effect = lambda key: {
            "executor": executor,
            "tenant_id": tenant_id,
        }.get(key)
        parent_data.inputs.biz_cc_id = biz_cc_id

        # Mock chunk_table_data fail
        mock_chunk_table_data.return_value = {"result": False, "message": "chunk failed"}

        # Mock client
        client = MagicMock()
        mock_get_client.return_value = client

        # Execute
        result = self.service.execute(data, parent_data)

        # Assertions
        self.assertFalse(result)
        data.set_outputs.assert_called_with("ex_data", "chunk failed")
