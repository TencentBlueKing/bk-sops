# -*- coding: utf-8 -*-
from django.test import TestCase
from mock import MagicMock, patch

from pipeline_plugins.components.collections.sites.open.cc.update_set.v1_0 import CCUpdateSetService, SelectMethod


class CCUpdateSetServiceV10TestCase(TestCase):
    def setUp(self):
        self.service = CCUpdateSetService()
        self.service.logger = MagicMock()

    def test_inputs_format(self):
        inputs = self.service.inputs_format()
        self.assertIsInstance(inputs, list)
        self.assertEqual(len(inputs), 6)

    def test_outputs_format(self):
        outputs = self.service.outputs_format()
        self.assertIsInstance(outputs, list)
        self.assertEqual(len(outputs), 0)

    @patch("pipeline_plugins.components.collections.sites.open.cc.update_set.v1_0.get_client_by_username")
    @patch("pipeline_plugins.components.collections.sites.open.cc.update_set.v1_0.cc_format_tree_set_id")
    def test_execute_topo_success(self, mock_format_tree, mock_get_client):
        # Mock inputs
        executor = "admin"
        tenant_id = "1"
        biz_cc_id = "2"
        cc_set_select_method = SelectMethod.TOPO.value
        cc_set_select_topo = ["100"]
        cc_set_property = "bk_set_name"
        cc_set_prop_value = "new_name"

        data = MagicMock()
        data.get_one_of_inputs.side_effect = lambda key, default=None: {
            "biz_cc_id": biz_cc_id,
            "cc_set_select_method": cc_set_select_method,
            "cc_set_select_topo": cc_set_select_topo,
            "cc_set_property": cc_set_property,
            "cc_set_prop_value": cc_set_prop_value,
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

        # Mock client
        client = MagicMock()
        mock_get_client.return_value = client
        client.api.update_set.return_value = {"result": True}

        # Execute
        result = self.service.execute(data, parent_data)

        # Assertions
        self.assertTrue(result)
        client.api.update_set.assert_called_once()
        call_args = client.api.update_set.call_args[0][0]
        self.assertEqual(call_args["bk_set_id"], 100)
        self.assertEqual(call_args["bk_set_name"], "new_name")

    @patch("pipeline_plugins.components.collections.sites.open.cc.update_set.v1_0.get_client_by_username")
    @patch("pipeline_plugins.components.collections.sites.open.cc.update_set.v1_0.cc_list_select_node_inst_id")
    def test_execute_text_success(self, mock_list_select, mock_get_client):
        # Mock inputs
        executor = "admin"
        tenant_id = "1"
        biz_cc_id = "2"
        cc_set_select_method = SelectMethod.TEXT.value
        cc_set_select_text = "Biz>Set"
        cc_set_property = "bk_set_name"
        cc_set_prop_value = "new_name"

        data = MagicMock()
        data.get_one_of_inputs.side_effect = lambda key, default=None: {
            "biz_cc_id": biz_cc_id,
            "cc_set_select_method": cc_set_select_method,
            "cc_set_select_text": cc_set_select_text,
            "cc_set_property": cc_set_property,
            "cc_set_prop_value": cc_set_prop_value,
        }.get(key, default)

        parent_data = MagicMock()
        parent_data.get_one_of_inputs.side_effect = lambda key: {
            "executor": executor,
            "tenant_id": tenant_id,
        }.get(key)
        parent_data.inputs.biz_cc_id = biz_cc_id

        # Mock helpers
        mock_list_select.return_value = {"result": True, "data": [100]}

        # Mock client
        client = MagicMock()
        mock_get_client.return_value = client
        client.api.update_set.return_value = {"result": True}

        # Execute
        result = self.service.execute(data, parent_data)

        # Assertions
        self.assertTrue(result)
        client.api.update_set.assert_called_once()
        call_args = client.api.update_set.call_args[0][0]
        self.assertEqual(call_args["bk_set_id"], 100)
        self.assertEqual(call_args["bk_set_name"], "new_name")

    @patch("pipeline_plugins.components.collections.sites.open.cc.update_set.v1_0.get_client_by_username")
    @patch("pipeline_plugins.components.collections.sites.open.cc.update_set.v1_0.cc_list_select_node_inst_id")
    def test_execute_text_fail(self, mock_list_select, mock_get_client):
        # Mock inputs
        executor = "admin"
        tenant_id = "1"
        biz_cc_id = "2"
        cc_set_select_method = SelectMethod.TEXT.value
        cc_set_select_text = "Biz>Set"

        data = MagicMock()
        data.get_one_of_inputs.side_effect = lambda key, default=None: {
            "biz_cc_id": biz_cc_id,
            "cc_set_select_method": cc_set_select_method,
            "cc_set_select_text": cc_set_select_text,
        }.get(key, default)

        parent_data = MagicMock()
        parent_data.get_one_of_inputs.side_effect = lambda key: {
            "executor": executor,
            "tenant_id": tenant_id,
        }.get(key)
        parent_data.inputs.biz_cc_id = biz_cc_id

        # Mock helpers
        mock_list_select.return_value = {"result": False, "message": "text fail"}

        # Mock client
        client = MagicMock()
        mock_get_client.return_value = client

        # Execute
        result = self.service.execute(data, parent_data)

        # Assertions
        self.assertFalse(result)
        data.set_outputs.assert_called_with("ex_data", "text fail")

    @patch("pipeline_plugins.components.collections.sites.open.cc.update_set.v1_0.get_client_by_username")
    def test_execute_invalid_method(self, mock_get_client):
        # Mock inputs
        executor = "admin"
        tenant_id = "1"
        biz_cc_id = "2"
        cc_set_select_method = "invalid"

        data = MagicMock()
        data.get_one_of_inputs.side_effect = lambda key, default=None: {
            "biz_cc_id": biz_cc_id,
            "cc_set_select_method": cc_set_select_method,
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

        # Execute
        result = self.service.execute(data, parent_data)

        # Assertions
        self.assertFalse(result)
        data.set_outputs.assert_called_with("ex_data", "请选择填参方式")

    @patch("pipeline_plugins.components.collections.sites.open.cc.update_set.v1_0.get_client_by_username")
    @patch("pipeline_plugins.components.collections.sites.open.cc.update_set.v1_0.cc_format_prop_data")
    @patch("pipeline_plugins.components.collections.sites.open.cc.update_set.v1_0.cc_format_tree_set_id")
    def test_execute_status_success(self, mock_format_tree, mock_format_prop, mock_get_client):
        # Mock inputs
        executor = "admin"
        tenant_id = "1"
        biz_cc_id = "2"
        cc_set_select_method = SelectMethod.TOPO.value
        cc_set_select_topo = ["100"]
        cc_set_property = "bk_service_status"
        cc_set_prop_value = "1"

        data = MagicMock()
        data.get_one_of_inputs.side_effect = lambda key, default=None: {
            "biz_cc_id": biz_cc_id,
            "cc_set_select_method": cc_set_select_method,
            "cc_set_select_topo": cc_set_select_topo,
            "cc_set_property": cc_set_property,
            "cc_set_prop_value": cc_set_prop_value,
        }.get(key, default)

        parent_data = MagicMock()
        parent_data.get_one_of_inputs.side_effect = lambda key: {
            "executor": executor,
            "tenant_id": tenant_id,
        }.get(key)
        parent_data.inputs.biz_cc_id = biz_cc_id

        # Mock helpers
        mock_format_tree.return_value = [100]
        mock_format_prop.return_value = {"result": True, "data": {"1": "开放"}}

        # Mock client
        client = MagicMock()
        mock_get_client.return_value = client
        client.api.update_set.return_value = {"result": True}

        # Execute
        result = self.service.execute(data, parent_data)

        # Assertions
        self.assertTrue(result)
        client.api.update_set.assert_called_once()
        call_args = client.api.update_set.call_args[0][0]
        self.assertEqual(call_args["bk_service_status"], "开放")

    @patch("pipeline_plugins.components.collections.sites.open.cc.update_set.v1_0.get_client_by_username")
    @patch("pipeline_plugins.components.collections.sites.open.cc.update_set.v1_0.cc_format_prop_data")
    @patch("pipeline_plugins.components.collections.sites.open.cc.update_set.v1_0.cc_format_tree_set_id")
    def test_execute_status_fail(self, mock_format_tree, mock_format_prop, mock_get_client):
        # Mock inputs
        executor = "admin"
        tenant_id = "1"
        biz_cc_id = "2"
        cc_set_select_method = SelectMethod.TOPO.value
        cc_set_select_topo = ["100"]
        cc_set_property = "bk_service_status"
        cc_set_prop_value = "invalid"

        data = MagicMock()
        data.get_one_of_inputs.side_effect = lambda key, default=None: {
            "biz_cc_id": biz_cc_id,
            "cc_set_select_method": cc_set_select_method,
            "cc_set_select_topo": cc_set_select_topo,
            "cc_set_property": cc_set_property,
            "cc_set_prop_value": cc_set_prop_value,
        }.get(key, default)

        parent_data = MagicMock()
        parent_data.get_one_of_inputs.side_effect = lambda key: {
            "executor": executor,
            "tenant_id": tenant_id,
        }.get(key)
        parent_data.inputs.biz_cc_id = biz_cc_id

        # Mock helpers
        mock_format_tree.return_value = [100]
        mock_format_prop.return_value = {"result": True, "data": {"1": "开放"}}

        # Mock client
        client = MagicMock()
        mock_get_client.return_value = client

        # Execute
        result = self.service.execute(data, parent_data)

        # Assertions
        self.assertFalse(result)
        data.set_outputs.assert_called_with("ex_data", "服务状态校验失败，请重试并修改为正确的服务状态")

    @patch("pipeline_plugins.components.collections.sites.open.cc.update_set.v1_0.get_client_by_username")
    @patch("pipeline_plugins.components.collections.sites.open.cc.update_set.v1_0.cc_format_prop_data")
    @patch("pipeline_plugins.components.collections.sites.open.cc.update_set.v1_0.cc_format_tree_set_id")
    def test_execute_env_success(self, mock_format_tree, mock_format_prop, mock_get_client):
        # Mock inputs
        executor = "admin"
        tenant_id = "1"
        biz_cc_id = "2"
        cc_set_select_method = SelectMethod.TOPO.value
        cc_set_select_topo = ["100"]
        cc_set_property = "bk_set_env"
        cc_set_prop_value = "1"

        data = MagicMock()
        data.get_one_of_inputs.side_effect = lambda key, default=None: {
            "biz_cc_id": biz_cc_id,
            "cc_set_select_method": cc_set_select_method,
            "cc_set_select_topo": cc_set_select_topo,
            "cc_set_property": cc_set_property,
            "cc_set_prop_value": cc_set_prop_value,
        }.get(key, default)

        parent_data = MagicMock()
        parent_data.get_one_of_inputs.side_effect = lambda key: {
            "executor": executor,
            "tenant_id": tenant_id,
        }.get(key)
        parent_data.inputs.biz_cc_id = biz_cc_id

        # Mock helpers
        mock_format_tree.return_value = [100]
        mock_format_prop.return_value = {"result": True, "data": {"1": "测试"}}

        # Mock client
        client = MagicMock()
        mock_get_client.return_value = client
        client.api.update_set.return_value = {"result": True}

        # Execute
        result = self.service.execute(data, parent_data)

        # Assertions
        self.assertTrue(result)
        client.api.update_set.assert_called_once()
        call_args = client.api.update_set.call_args[0][0]
        self.assertEqual(call_args["bk_set_env"], "测试")

    @patch("pipeline_plugins.components.collections.sites.open.cc.update_set.v1_0.get_client_by_username")
    @patch("pipeline_plugins.components.collections.sites.open.cc.update_set.v1_0.cc_format_prop_data")
    @patch("pipeline_plugins.components.collections.sites.open.cc.update_set.v1_0.cc_format_tree_set_id")
    def test_execute_env_fail(self, mock_format_tree, mock_format_prop, mock_get_client):
        # Mock inputs
        executor = "admin"
        tenant_id = "1"
        biz_cc_id = "2"
        cc_set_select_method = SelectMethod.TOPO.value
        cc_set_select_topo = ["100"]
        cc_set_property = "bk_set_env"
        cc_set_prop_value = "invalid"

        data = MagicMock()
        data.get_one_of_inputs.side_effect = lambda key, default=None: {
            "biz_cc_id": biz_cc_id,
            "cc_set_select_method": cc_set_select_method,
            "cc_set_select_topo": cc_set_select_topo,
            "cc_set_property": cc_set_property,
            "cc_set_prop_value": cc_set_prop_value,
        }.get(key, default)

        parent_data = MagicMock()
        parent_data.get_one_of_inputs.side_effect = lambda key: {
            "executor": executor,
            "tenant_id": tenant_id,
        }.get(key)
        parent_data.inputs.biz_cc_id = biz_cc_id

        # Mock helpers
        mock_format_tree.return_value = [100]
        mock_format_prop.return_value = {"result": True, "data": {"1": "测试"}}

        # Mock client
        client = MagicMock()
        mock_get_client.return_value = client

        # Execute
        result = self.service.execute(data, parent_data)

        # Assertions
        self.assertFalse(result)
        data.set_outputs.assert_called_with("ex_data", "环境类型校验失败，请重试并修改为正确的环境类型")

    @patch("pipeline_plugins.components.collections.sites.open.cc.update_set.v1_0.get_client_by_username")
    @patch("pipeline_plugins.components.collections.sites.open.cc.update_set.v1_0.cc_format_tree_set_id")
    def test_execute_capacity_success(self, mock_format_tree, mock_get_client):
        # Mock inputs
        executor = "admin"
        tenant_id = "1"
        biz_cc_id = "2"
        cc_set_select_method = SelectMethod.TOPO.value
        cc_set_select_topo = ["100"]
        cc_set_property = "bk_capacity"
        cc_set_prop_value = "1000"

        data = MagicMock()
        data.get_one_of_inputs.side_effect = lambda key, default=None: {
            "biz_cc_id": biz_cc_id,
            "cc_set_select_method": cc_set_select_method,
            "cc_set_select_topo": cc_set_select_topo,
            "cc_set_property": cc_set_property,
            "cc_set_prop_value": cc_set_prop_value,
        }.get(key, default)

        parent_data = MagicMock()
        parent_data.get_one_of_inputs.side_effect = lambda key: {
            "executor": executor,
            "tenant_id": tenant_id,
        }.get(key)
        parent_data.inputs.biz_cc_id = biz_cc_id

        # Mock helpers
        mock_format_tree.return_value = [100]

        # Mock client
        client = MagicMock()
        mock_get_client.return_value = client
        client.api.update_set.return_value = {"result": True}

        # Execute
        result = self.service.execute(data, parent_data)

        # Assertions
        self.assertTrue(result)
        client.api.update_set.assert_called_once()
        call_args = client.api.update_set.call_args[0][0]
        self.assertEqual(call_args["bk_capacity"], 1000)

    @patch("pipeline_plugins.components.collections.sites.open.cc.update_set.v1_0.get_client_by_username")
    @patch("pipeline_plugins.components.collections.sites.open.cc.update_set.v1_0.cc_format_tree_set_id")
    def test_execute_capacity_fail(self, mock_format_tree, mock_get_client):
        # Mock inputs
        executor = "admin"
        tenant_id = "1"
        biz_cc_id = "2"
        cc_set_select_method = SelectMethod.TOPO.value
        cc_set_select_topo = ["100"]
        cc_set_property = "bk_capacity"
        cc_set_prop_value = "invalid"

        data = MagicMock()
        data.get_one_of_inputs.side_effect = lambda key, default=None: {
            "biz_cc_id": biz_cc_id,
            "cc_set_select_method": cc_set_select_method,
            "cc_set_select_topo": cc_set_select_topo,
            "cc_set_property": cc_set_property,
            "cc_set_prop_value": cc_set_prop_value,
        }.get(key, default)

        parent_data = MagicMock()
        parent_data.get_one_of_inputs.side_effect = lambda key: {
            "executor": executor,
            "tenant_id": tenant_id,
        }.get(key)
        parent_data.inputs.biz_cc_id = biz_cc_id

        # Mock helpers
        mock_format_tree.return_value = [100]

        # Mock client
        client = MagicMock()
        mock_get_client.return_value = client

        # Execute
        result = self.service.execute(data, parent_data)

        # Assertions
        self.assertFalse(result)
        data.set_outputs.assert_called_with("ex_data", "集群容量必须为整数")

    @patch("pipeline_plugins.components.collections.sites.open.cc.update_set.v1_0.get_client_by_username")
    @patch("pipeline_plugins.components.collections.sites.open.cc.update_set.v1_0.cc_format_prop_data")
    @patch("pipeline_plugins.components.collections.sites.open.cc.update_set.v1_0.cc_format_tree_set_id")
    def test_execute_prop_fail(self, mock_format_tree, mock_format_prop, mock_get_client):
        # Mock inputs
        executor = "admin"
        tenant_id = "1"
        biz_cc_id = "2"
        cc_set_select_method = SelectMethod.TOPO.value
        cc_set_select_topo = ["100"]
        cc_set_property = "bk_service_status"
        cc_set_prop_value = "1"

        data = MagicMock()
        data.get_one_of_inputs.side_effect = lambda key, default=None: {
            "biz_cc_id": biz_cc_id,
            "cc_set_select_method": cc_set_select_method,
            "cc_set_select_topo": cc_set_select_topo,
            "cc_set_property": cc_set_property,
            "cc_set_prop_value": cc_set_prop_value,
        }.get(key, default)

        parent_data = MagicMock()
        parent_data.get_one_of_inputs.side_effect = lambda key: {
            "executor": executor,
            "tenant_id": tenant_id,
        }.get(key)
        parent_data.inputs.biz_cc_id = biz_cc_id

        # Mock helpers
        mock_format_tree.return_value = [100]
        mock_format_prop.return_value = {"result": False, "message": "prop fail"}

        # Mock client
        client = MagicMock()
        mock_get_client.return_value = client

        # Execute
        result = self.service.execute(data, parent_data)

        # Assertions
        self.assertFalse(result)
        data.set_outputs.assert_called_with("ex_data", "prop fail")

    @patch("pipeline_plugins.components.collections.sites.open.cc.update_set.v1_0.get_client_by_username")
    @patch("pipeline_plugins.components.collections.sites.open.cc.update_set.v1_0.cc_format_tree_set_id")
    def test_execute_update_fail(self, mock_format_tree, mock_get_client):
        # Mock inputs
        executor = "admin"
        tenant_id = "1"
        biz_cc_id = "2"
        cc_set_select_method = SelectMethod.TOPO.value
        cc_set_select_topo = ["100"]
        cc_set_property = "bk_set_name"
        cc_set_prop_value = "new_name"

        data = MagicMock()
        data.get_one_of_inputs.side_effect = lambda key, default=None: {
            "biz_cc_id": biz_cc_id,
            "cc_set_select_method": cc_set_select_method,
            "cc_set_select_topo": cc_set_select_topo,
            "cc_set_property": cc_set_property,
            "cc_set_prop_value": cc_set_prop_value,
        }.get(key, default)

        parent_data = MagicMock()
        parent_data.get_one_of_inputs.side_effect = lambda key: {
            "executor": executor,
            "tenant_id": tenant_id,
        }.get(key)
        parent_data.inputs.biz_cc_id = biz_cc_id

        # Mock helpers
        mock_format_tree.return_value = [100]

        # Mock client
        client = MagicMock()
        mock_get_client.return_value = client
        client.api.update_set.return_value = {"result": False, "message": "update fail"}

        # Execute
        result = self.service.execute(data, parent_data)

        # Assertions
        self.assertFalse(result)
        data.set_outputs.assert_called()
        args, _ = data.set_outputs.call_args
        self.assertIn("update fail", args[1])
