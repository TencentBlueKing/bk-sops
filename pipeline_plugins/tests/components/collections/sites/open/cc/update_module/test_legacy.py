# -*- coding: utf-8 -*-
from django.test import TestCase
from mock import MagicMock, patch

from pipeline_plugins.components.collections.sites.open.cc.update_module.legacy import CCUpdateModuleService


class CCUpdateModuleServiceLegacyTestCase(TestCase):
    def setUp(self):
        self.service = CCUpdateModuleService()
        self.service.logger = MagicMock()

    def test_inputs_format(self):
        inputs = self.service.inputs_format()
        self.assertIsInstance(inputs, list)
        self.assertEqual(len(inputs), 4)

    def test_outputs_format(self):
        outputs = self.service.outputs_format()
        self.assertIsInstance(outputs, list)
        self.assertEqual(len(outputs), 0)

    @patch("pipeline_plugins.components.collections.sites.open.cc.update_module.legacy.get_client_by_username")
    @patch("pipeline_plugins.components.collections.sites.open.cc.update_module.legacy.cc_format_prop_data")
    @patch("pipeline_plugins.components.collections.sites.open.cc.update_module.legacy.cc_format_tree_mode_id")
    @patch("pipeline_plugins.components.collections.sites.open.cc.update_module.legacy.get_module_set_id")
    def test_execute_success(self, mock_get_set_id, mock_format_tree, mock_format_prop, mock_get_client):
        # Mock inputs
        executor = "admin"
        tenant_id = "1"
        biz_cc_id = "2"
        cc_module_select = ["100"]
        cc_module_property = "bk_module_type"
        cc_module_prop_value = "1"

        data = MagicMock()
        data.get_one_of_inputs.side_effect = lambda key, default=None: {
            "biz_cc_id": biz_cc_id,
            "cc_module_select": cc_module_select,
            "cc_module_property": cc_module_property,
            "cc_module_prop_value": cc_module_prop_value,
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
        mock_format_prop.return_value = {"result": True, "data": {"1": "test"}}
        mock_get_set_id.return_value = 10

        # Mock client
        client = MagicMock()
        mock_get_client.return_value = client
        client.api.search_biz_inst_topo.return_value = {"result": True, "data": []}
        client.api.update_module.return_value = {"result": True}

        # Execute
        result = self.service.execute(data, parent_data)

        # Assertions
        self.assertTrue(result)
        client.api.update_module.assert_called_once()
        call_args = client.api.update_module.call_args[0][0]
        self.assertEqual(call_args["bk_module_id"], 100)
        self.assertEqual(call_args["bk_module_type"], "test")

    @patch("pipeline_plugins.components.collections.sites.open.cc.update_module.legacy.get_client_by_username")
    def test_execute_topo_fail(self, mock_get_client):
        # Mock inputs
        executor = "admin"
        tenant_id = "1"
        biz_cc_id = "2"

        data = MagicMock()
        data.get_one_of_inputs.side_effect = lambda key, default=None: {
            "biz_cc_id": biz_cc_id,
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
        client.api.search_biz_inst_topo.return_value = {"result": False, "message": "topo fail"}

        # Execute
        result = self.service.execute(data, parent_data)

        # Assertions
        self.assertFalse(result)
        data.set_outputs.assert_called()
        args, _ = data.set_outputs.call_args
        self.assertEqual(args[0], "ex_data")
        self.assertIn("topo fail", args[1])

    @patch("pipeline_plugins.components.collections.sites.open.cc.update_module.legacy.get_client_by_username")
    @patch("pipeline_plugins.components.collections.sites.open.cc.update_module.legacy.cc_format_prop_data")
    @patch("pipeline_plugins.components.collections.sites.open.cc.update_module.legacy.cc_format_tree_mode_id")
    def test_execute_type_fail(self, mock_format_tree, mock_format_prop, mock_get_client):
        # Mock inputs
        executor = "admin"
        tenant_id = "1"
        biz_cc_id = "2"
        cc_module_select = ["100"]
        cc_module_property = "bk_module_type"
        cc_module_prop_value = "invalid"

        data = MagicMock()
        data.get_one_of_inputs.side_effect = lambda key, default=None: {
            "biz_cc_id": biz_cc_id,
            "cc_module_select": cc_module_select,
            "cc_module_property": cc_module_property,
            "cc_module_prop_value": cc_module_prop_value,
        }.get(key, default)

        parent_data = MagicMock()
        parent_data.get_one_of_inputs.side_effect = lambda key: {
            "executor": executor,
            "tenant_id": tenant_id,
        }.get(key)
        parent_data.inputs.biz_cc_id = biz_cc_id

        # Mock helpers
        mock_format_tree.return_value = [100]
        mock_format_prop.return_value = {"result": True, "data": {"1": "test"}}

        # Mock client
        client = MagicMock()
        mock_get_client.return_value = client
        client.api.search_biz_inst_topo.return_value = {"result": True, "data": []}

        # Execute
        result = self.service.execute(data, parent_data)

        # Assertions
        self.assertFalse(result)
        data.set_outputs.assert_called_with("ex_data", "模块类型校验失败，请重试并填写正确的模块类型")

    @patch("pipeline_plugins.components.collections.sites.open.cc.update_module.legacy.get_client_by_username")
    @patch("pipeline_plugins.components.collections.sites.open.cc.update_module.legacy.cc_format_prop_data")
    @patch("pipeline_plugins.components.collections.sites.open.cc.update_module.legacy.cc_format_tree_mode_id")
    def test_execute_prop_fail(self, mock_format_tree, mock_format_prop, mock_get_client):
        # Mock inputs
        executor = "admin"
        tenant_id = "1"
        biz_cc_id = "2"
        cc_module_select = ["100"]
        cc_module_property = "bk_module_type"
        cc_module_prop_value = "1"

        data = MagicMock()
        data.get_one_of_inputs.side_effect = lambda key, default=None: {
            "biz_cc_id": biz_cc_id,
            "cc_module_select": cc_module_select,
            "cc_module_property": cc_module_property,
            "cc_module_prop_value": cc_module_prop_value,
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
        client.api.search_biz_inst_topo.return_value = {"result": True, "data": []}

        # Execute
        result = self.service.execute(data, parent_data)

        # Assertions
        self.assertFalse(result)
        data.set_outputs.assert_called_with("ex_data", "prop fail")

    @patch("pipeline_plugins.components.collections.sites.open.cc.update_module.legacy.get_client_by_username")
    @patch("pipeline_plugins.components.collections.sites.open.cc.update_module.legacy.cc_format_tree_mode_id")
    @patch("pipeline_plugins.components.collections.sites.open.cc.update_module.legacy.get_module_set_id")
    def test_execute_update_fail(self, mock_get_set_id, mock_format_tree, mock_get_client):
        # Mock inputs
        executor = "admin"
        tenant_id = "1"
        biz_cc_id = "2"
        cc_module_select = ["100"]
        cc_module_property = "other"
        cc_module_prop_value = "val"

        data = MagicMock()
        data.get_one_of_inputs.side_effect = lambda key, default=None: {
            "biz_cc_id": biz_cc_id,
            "cc_module_select": cc_module_select,
            "cc_module_property": cc_module_property,
            "cc_module_prop_value": cc_module_prop_value,
        }.get(key, default)

        parent_data = MagicMock()
        parent_data.get_one_of_inputs.side_effect = lambda key: {
            "executor": executor,
            "tenant_id": tenant_id,
        }.get(key)
        parent_data.inputs.biz_cc_id = biz_cc_id

        # Mock helpers
        mock_format_tree.return_value = [100]
        mock_get_set_id.return_value = 10

        # Mock client
        client = MagicMock()
        mock_get_client.return_value = client
        client.api.search_biz_inst_topo.return_value = {"result": True, "data": []}
        client.api.update_module.return_value = {"result": False, "message": "update fail"}

        # Execute
        result = self.service.execute(data, parent_data)

        # Assertions
        self.assertFalse(result)
        data.set_outputs.assert_called()
        args, _ = data.set_outputs.call_args
        self.assertEqual(args[0], "ex_data")
        self.assertIn("update fail", args[1])
