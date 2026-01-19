# -*- coding: utf-8 -*-
from django.test import TestCase
from mock import MagicMock, patch

from pipeline_plugins.components.collections.sites.open.cc.create_set.v1_0 import CCCreateSetService, chunk_table_data


class CCCreateSetServiceV10TestCase(TestCase):
    def setUp(self):
        self.service = CCCreateSetService()
        self.service.logger = MagicMock()

    @patch("pipeline_plugins.components.collections.sites.open.cc.create_set.v1_0.get_client_by_username")
    @patch("pipeline_plugins.components.collections.sites.open.cc.create_set.v1_0.cc_format_prop_data")
    @patch("pipeline_plugins.components.collections.sites.open.cc.create_set.v1_0.cc_format_tree_mode_id")
    def test_execute_success(self, mock_format_tree, mock_format_prop, mock_get_client):
        # Mock inputs
        executor = "admin"
        tenant_id = "1"
        biz_cc_id = "2"
        cc_set_parent_select = ["100"]
        cc_set_info = [{"bk_set_name": "set1", "bk_set_env": "3", "bk_service_status": "1", "bk_capacity": "100"}]

        data = MagicMock()
        data.get_one_of_inputs.side_effect = lambda key, default=None: {
            "biz_cc_id": biz_cc_id,
            "cc_set_parent_select": cc_set_parent_select,
            "cc_set_info": cc_set_info,
        }.get(key, default)

        parent_data = MagicMock()
        parent_data.get_one_of_inputs.side_effect = lambda key: {
            "executor": executor,
            "tenant_id": tenant_id,
            "language": "zh-cn",
        }.get(key)
        parent_data.inputs.biz_cc_id = biz_cc_id

        # Mock helpers
        mock_format_tree.return_value = [100]
        mock_format_prop.side_effect = [
            {"result": True, "data": {"test": "3"}},  # bk_set_env
            {"result": True, "data": {"test": "1"}},  # bk_service_status
        ]

        # Mock client
        client = MagicMock()
        mock_get_client.return_value = client
        client.api.create_set.return_value = {"result": True}

        # Execute
        result = self.service.execute(data, parent_data)

        # Assertions
        self.assertTrue(result)
        client.api.create_set.assert_called_once()
        call_args = client.api.create_set.call_args[0][0]
        self.assertEqual(call_args["bk_set_name"], "set1")
        self.assertEqual(call_args["bk_parent_id"], 100)
        self.assertEqual(call_args["bk_biz_id"], biz_cc_id)

    @patch("pipeline_plugins.components.collections.sites.open.cc.create_set.v1_0.get_client_by_username")
    @patch("pipeline_plugins.components.collections.sites.open.cc.create_set.v1_0.cc_format_prop_data")
    @patch("pipeline_plugins.components.collections.sites.open.cc.create_set.v1_0.cc_format_tree_mode_id")
    def test_execute_chunk_success(self, mock_format_tree, mock_format_prop, mock_get_client):
        # Mock inputs
        executor = "admin"
        tenant_id = "1"
        biz_cc_id = "2"
        cc_set_parent_select = ["100"]
        cc_set_info = [{"bk_set_name": "set1\nset2", "bk_set_env": "3", "bk_service_status": "1", "bk_capacity": "100"}]

        data = MagicMock()
        data.get_one_of_inputs.side_effect = lambda key, default=None: {
            "biz_cc_id": biz_cc_id,
            "cc_set_parent_select": cc_set_parent_select,
            "cc_set_info": cc_set_info,
        }.get(key, default)

        parent_data = MagicMock()
        parent_data.get_one_of_inputs.side_effect = lambda key: {
            "executor": executor,
            "tenant_id": tenant_id,
        }.get(key)
        parent_data.inputs.biz_cc_id = biz_cc_id

        mock_format_tree.return_value = [100]
        mock_format_prop.side_effect = [
            {"result": True, "data": {"test": "3"}},  # bk_set_env
            {"result": True, "data": {"test": "1"}},  # bk_service_status
        ]

        client = MagicMock()
        mock_get_client.return_value = client
        client.api.create_set.return_value = {"result": True}

        # Execute
        result = self.service.execute(data, parent_data)

        # Assertions
        self.assertTrue(result)
        self.assertEqual(client.api.create_set.call_count, 2)

    @patch("pipeline_plugins.components.collections.sites.open.cc.create_set.v1_0.get_client_by_username")
    @patch("pipeline_plugins.components.collections.sites.open.cc.create_set.v1_0.cc_format_prop_data")
    @patch("pipeline_plugins.components.collections.sites.open.cc.create_set.v1_0.cc_format_tree_mode_id")
    def test_execute_chunk_fail(self, mock_format_tree, mock_format_prop, mock_get_client):
        # Mock inputs
        executor = "admin"
        tenant_id = "1"
        biz_cc_id = "2"
        cc_set_parent_select = ["100"]
        cc_set_info = [{"bk_set_name": "set1\nset2", "bk_set_env": "3\n4\n5", "bk_service_status": "1"}]

        data = MagicMock()
        data.get_one_of_inputs.side_effect = lambda key, default=None: {
            "biz_cc_id": biz_cc_id,
            "cc_set_parent_select": cc_set_parent_select,
            "cc_set_info": cc_set_info,
        }.get(key, default)

        parent_data = MagicMock()
        parent_data.get_one_of_inputs.side_effect = lambda key: {
            "executor": executor,
            "tenant_id": tenant_id,
        }.get(key)
        parent_data.inputs.biz_cc_id = biz_cc_id

        mock_format_tree.return_value = [100]
        mock_format_prop.side_effect = [
            {"result": True, "data": {"test": "3"}},  # bk_set_env
            {"result": True, "data": {"test": "1"}},  # bk_service_status
        ]

        mock_get_client.return_value = MagicMock()

        # Execute
        result = self.service.execute(data, parent_data)

        # Assertions
        self.assertFalse(result)
        data.set_outputs.assert_called()
        args, _ = data.set_outputs.call_args
        self.assertEqual(args[0], "ex_data")
        self.assertIn("行数不一致", args[1])

    @patch("pipeline_plugins.components.collections.sites.open.cc.create_set.v1_0.get_client_by_username")
    @patch("pipeline_plugins.components.collections.sites.open.cc.create_set.v1_0.cc_format_prop_data")
    @patch("pipeline_plugins.components.collections.sites.open.cc.create_set.v1_0.cc_format_tree_mode_id")
    def test_execute_env_fail(self, mock_format_tree, mock_format_prop, mock_get_client):
        # Mock inputs
        executor = "admin"
        tenant_id = "1"
        biz_cc_id = "2"
        cc_set_parent_select = ["100"]
        cc_set_info = [{"bk_set_name": "set1", "bk_set_env": "invalid", "bk_service_status": "1"}]

        data = MagicMock()
        data.get_one_of_inputs.side_effect = lambda key, default=None: {
            "biz_cc_id": biz_cc_id,
            "cc_set_parent_select": cc_set_parent_select,
            "cc_set_info": cc_set_info,
        }.get(key, default)

        parent_data = MagicMock()
        parent_data.get_one_of_inputs.side_effect = lambda key: {
            "executor": executor,
            "tenant_id": tenant_id,
        }.get(key)
        parent_data.inputs.biz_cc_id = biz_cc_id

        mock_format_tree.return_value = [100]
        mock_format_prop.side_effect = [
            {"result": True, "data": {"test": "3"}},  # bk_set_env
            {"result": True, "data": {"test": "1"}},  # bk_service_status
        ]

        mock_get_client.return_value = MagicMock()

        # Execute
        result = self.service.execute(data, parent_data)

        # Assertions
        self.assertFalse(result)
        data.set_outputs.assert_called_with("ex_data", "环境类型校验失败，请重试并修改为正确的环境类型")

    @patch("pipeline_plugins.components.collections.sites.open.cc.create_set.v1_0.get_client_by_username")
    @patch("pipeline_plugins.components.collections.sites.open.cc.create_set.v1_0.cc_format_prop_data")
    @patch("pipeline_plugins.components.collections.sites.open.cc.create_set.v1_0.cc_format_tree_mode_id")
    def test_execute_status_fail(self, mock_format_tree, mock_format_prop, mock_get_client):
        # Mock inputs
        executor = "admin"
        tenant_id = "1"
        biz_cc_id = "2"
        cc_set_parent_select = ["100"]
        cc_set_info = [{"bk_set_name": "set1", "bk_set_env": "3", "bk_service_status": "invalid"}]

        data = MagicMock()
        data.get_one_of_inputs.side_effect = lambda key, default=None: {
            "biz_cc_id": biz_cc_id,
            "cc_set_parent_select": cc_set_parent_select,
            "cc_set_info": cc_set_info,
        }.get(key, default)

        parent_data = MagicMock()
        parent_data.get_one_of_inputs.side_effect = lambda key: {
            "executor": executor,
            "tenant_id": tenant_id,
        }.get(key)
        parent_data.inputs.biz_cc_id = biz_cc_id

        mock_format_tree.return_value = [100]
        mock_format_prop.side_effect = [
            {"result": True, "data": {"test": "3"}},  # bk_set_env
            {"result": True, "data": {"test": "1"}},  # bk_service_status
        ]

        mock_get_client.return_value = MagicMock()

        # Execute
        result = self.service.execute(data, parent_data)

        # Assertions
        self.assertFalse(result)
        data.set_outputs.assert_called_with("ex_data", "服务状态校验失败，请重试并修改为正确的服务状态")

    @patch("pipeline_plugins.components.collections.sites.open.cc.create_set.v1_0.get_client_by_username")
    @patch("pipeline_plugins.components.collections.sites.open.cc.create_set.v1_0.cc_format_prop_data")
    @patch("pipeline_plugins.components.collections.sites.open.cc.create_set.v1_0.cc_format_tree_mode_id")
    def test_execute_capacity_fail(self, mock_format_tree, mock_format_prop, mock_get_client):
        # Mock inputs
        executor = "admin"
        tenant_id = "1"
        biz_cc_id = "2"
        cc_set_parent_select = ["100"]
        cc_set_info = [{"bk_set_name": "set1", "bk_set_env": "3", "bk_service_status": "1", "bk_capacity": "invalid"}]

        data = MagicMock()
        data.get_one_of_inputs.side_effect = lambda key, default=None: {
            "biz_cc_id": biz_cc_id,
            "cc_set_parent_select": cc_set_parent_select,
            "cc_set_info": cc_set_info,
        }.get(key, default)

        parent_data = MagicMock()
        parent_data.get_one_of_inputs.side_effect = lambda key: {
            "executor": executor,
            "tenant_id": tenant_id,
        }.get(key)
        parent_data.inputs.biz_cc_id = biz_cc_id

        mock_format_tree.return_value = [100]
        mock_format_prop.side_effect = [
            {"result": True, "data": {"test": "3"}},  # bk_set_env
            {"result": True, "data": {"test": "1"}},  # bk_service_status
        ]

        mock_get_client.return_value = MagicMock()

        # Execute
        result = self.service.execute(data, parent_data)

        # Assertions
        self.assertFalse(result)
        data.set_outputs.assert_called_with("ex_data", "集群容量必须为整数")

    @patch("pipeline_plugins.components.collections.sites.open.cc.create_set.v1_0.get_client_by_username")
    @patch("pipeline_plugins.components.collections.sites.open.cc.create_set.v1_0.cc_format_prop_data")
    @patch("pipeline_plugins.components.collections.sites.open.cc.create_set.v1_0.cc_format_tree_mode_id")
    def test_execute_create_fail(self, mock_format_tree, mock_format_prop, mock_get_client):
        # Mock inputs
        executor = "admin"
        tenant_id = "1"
        biz_cc_id = "2"
        cc_set_parent_select = ["100"]
        cc_set_info = [{"bk_set_name": "set1", "bk_set_env": "3", "bk_service_status": "1"}]

        data = MagicMock()
        data.get_one_of_inputs.side_effect = lambda key, default=None: {
            "biz_cc_id": biz_cc_id,
            "cc_set_parent_select": cc_set_parent_select,
            "cc_set_info": cc_set_info,
        }.get(key, default)

        parent_data = MagicMock()
        parent_data.get_one_of_inputs.side_effect = lambda key: {
            "executor": executor,
            "tenant_id": tenant_id,
        }.get(key)
        parent_data.inputs.biz_cc_id = biz_cc_id

        mock_format_tree.return_value = [100]
        mock_format_prop.side_effect = [
            {"result": True, "data": {"test": "3"}},  # bk_set_env
            {"result": True, "data": {"test": "1"}},  # bk_service_status
        ]

        client = MagicMock()
        mock_get_client.return_value = client
        client.api.create_set.return_value = {"result": False, "message": "create failed"}

        # Execute
        result = self.service.execute(data, parent_data)

        # Assertions
        self.assertFalse(result)
        data.set_outputs.assert_called()
        args, _ = data.set_outputs.call_args
        self.assertEqual(args[0], "ex_data")
        self.assertIn("create failed", args[1])

    @patch("pipeline_plugins.components.collections.sites.open.cc.create_set.v1_0.get_client_by_username")
    @patch("pipeline_plugins.components.collections.sites.open.cc.create_set.v1_0.cc_format_prop_data")
    @patch("pipeline_plugins.components.collections.sites.open.cc.create_set.v1_0.cc_format_tree_mode_id")
    def test_execute_prop_env_fail(self, mock_format_tree, mock_format_prop, mock_get_client):
        # Mock inputs
        executor = "admin"
        tenant_id = "1"
        biz_cc_id = "2"
        cc_set_parent_select = ["100"]
        cc_set_info = []

        data = MagicMock()
        data.get_one_of_inputs.side_effect = lambda key, default=None: {
            "biz_cc_id": biz_cc_id,
            "cc_set_parent_select": cc_set_parent_select,
            "cc_set_info": cc_set_info,
        }.get(key, default)

        parent_data = MagicMock()
        parent_data.get_one_of_inputs.side_effect = lambda key: {
            "executor": executor,
            "tenant_id": tenant_id,
        }.get(key)
        parent_data.inputs.biz_cc_id = biz_cc_id

        mock_format_tree.return_value = [100]
        mock_format_prop.return_value = {"result": False, "message": "prop env failed"}

        mock_get_client.return_value = MagicMock()

        # Execute
        result = self.service.execute(data, parent_data)

        # Assertions
        self.assertFalse(result)
        data.set_outputs.assert_called_with("ex_data", "prop env failed")

    @patch("pipeline_plugins.components.collections.sites.open.cc.create_set.v1_0.get_client_by_username")
    @patch("pipeline_plugins.components.collections.sites.open.cc.create_set.v1_0.cc_format_prop_data")
    @patch("pipeline_plugins.components.collections.sites.open.cc.create_set.v1_0.cc_format_tree_mode_id")
    def test_execute_prop_status_fail(self, mock_format_tree, mock_format_prop, mock_get_client):
        # Mock inputs
        executor = "admin"
        tenant_id = "1"
        biz_cc_id = "2"
        cc_set_parent_select = ["100"]
        cc_set_info = []

        data = MagicMock()
        data.get_one_of_inputs.side_effect = lambda key, default=None: {
            "biz_cc_id": biz_cc_id,
            "cc_set_parent_select": cc_set_parent_select,
            "cc_set_info": cc_set_info,
        }.get(key, default)

        parent_data = MagicMock()
        parent_data.get_one_of_inputs.side_effect = lambda key: {
            "executor": executor,
            "tenant_id": tenant_id,
        }.get(key)
        parent_data.inputs.biz_cc_id = biz_cc_id

        mock_format_tree.return_value = [100]
        mock_format_prop.side_effect = [
            {"result": True, "data": {"test": "3"}},  # bk_set_env success
            {"result": False, "message": "prop status failed"},  # bk_service_status fail
        ]

        mock_get_client.return_value = MagicMock()

        # Execute
        result = self.service.execute(data, parent_data)

        # Assertions
        self.assertFalse(result)
        data.set_outputs.assert_called_with("ex_data", "prop status failed")

    def test_chunk_table_data_int(self):
        column = {"key": 123}
        result = chunk_table_data(column)
        self.assertTrue(result["result"])
        self.assertEqual(result["data"][0]["key"], 123)

    def test_chunk_table_data_invalid_type(self):
        column = {"key": []}
        result = chunk_table_data(column)
        self.assertFalse(result["result"])
        self.assertIn("格式错误", result["message"])

    def test_inputs_format(self):
        inputs = self.service.inputs_format()
        self.assertIsInstance(inputs, list)
        self.assertEqual(len(inputs), 3)

    def test_outputs_format(self):
        outputs = self.service.outputs_format()
        self.assertIsInstance(outputs, list)
        self.assertEqual(len(outputs), 0)
