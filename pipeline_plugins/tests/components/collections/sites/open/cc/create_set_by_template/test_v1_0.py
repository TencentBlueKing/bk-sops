# -*- coding: utf-8 -*-
from django.test import TestCase
from mock import MagicMock, patch

from pipeline_plugins.components.collections.sites.open.cc.create_set_by_template.v1_0 import (
    CCCreateSetBySetTemplateService,
)


class CCCreateSetBySetTemplateServiceTestCase(TestCase):
    def setUp(self):
        self.service = CCCreateSetBySetTemplateService()
        self.service.logger = MagicMock()

    def test_inputs_format(self):
        inputs = self.service.inputs_format()
        self.assertEqual(len(inputs), 6)

    @patch("pipeline_plugins.components.collections.sites.open.cc.create_set_by_template.v1_0.cc_format_tree_mode_id")
    @patch("pipeline_plugins.components.collections.sites.open.cc.create_set_by_template.v1_0.get_client_by_username")
    def test_execute_topo_success(self, mock_get_client, mock_cc_format_tree_mode_id):
        # Prepare
        executor = "admin"
        tenant_id = "tenant_1"
        biz_cc_id = "1"
        cc_set_names = "set1,set2"
        cc_set_template = "100"

        parent_data = MagicMock()
        parent_data.get_one_of_inputs.side_effect = lambda key: {
            "executor": executor,
            "tenant_id": tenant_id,
        }.get(key)
        parent_data.inputs.biz_cc_id = biz_cc_id

        data = MagicMock()
        data.get_one_of_inputs.side_effect = lambda key, default=None: {
            "biz_cc_id": biz_cc_id,
            "cc_select_set_parent_method": "topo",
            "cc_set_parent_select_topo": [1],
            "cc_set_name": cc_set_names,
            "cc_set_template": cc_set_template,
            "cc_set_attr": [],
        }.get(key, default)

        mock_client = MagicMock()

        call_args_captured = []

        def side_effect(*args, **kwargs):
            import copy

            call_args_captured.append((copy.deepcopy(args), copy.deepcopy(kwargs)))
            return {"result": True, "data": {"bk_set_id": 10}, "message": "success"}

        mock_client.api.create_set.side_effect = side_effect
        mock_get_client.return_value = mock_client

        mock_cc_format_tree_mode_id.return_value = [1]

        # Act
        result = self.service.execute(data, parent_data)

        # Assert
        self.assertTrue(result)
        self.assertEqual(mock_client.api.create_set.call_count, 2)

        self.assertEqual(call_args_captured[0][0][0]["bk_set_name"], "set1")
        self.assertEqual(call_args_captured[1][0][0]["bk_set_name"], "set2")

    @patch(
        "pipeline_plugins.components.collections.sites.open.cc.create_set_by_template.v1_0.cc_list_select_node_inst_id"
    )
    @patch("pipeline_plugins.components.collections.sites.open.cc.create_set_by_template.v1_0.get_client_by_username")
    def test_execute_text_success(self, mock_get_client, mock_cc_list_select_node_inst_id):
        # Prepare
        parent_data = MagicMock()
        parent_data.get_one_of_inputs.side_effect = lambda key: {
            "executor": "admin",
            "tenant_id": "tenant_1",
        }.get(key)

        data = MagicMock()
        data.get_one_of_inputs.side_effect = lambda key, default=None: {
            "biz_cc_id": "1",
            "cc_select_set_parent_method": "text",
            "cc_set_parent_select_text": "path",
            "cc_set_name": "set1",
            "cc_set_template": "100",
        }.get(key, default)

        mock_client = MagicMock()
        mock_client.api.create_set.return_value = {"result": True, "data": {}}
        mock_get_client.return_value = mock_client

        mock_cc_list_select_node_inst_id.return_value = {"result": True, "data": [2]}

        # Act
        result = self.service.execute(data, parent_data)

        # Assert
        self.assertTrue(result)
        mock_cc_list_select_node_inst_id.assert_called_once()
        mock_client.api.create_set.assert_called_once()
        self.assertEqual(mock_client.api.create_set.call_args[0][0]["bk_parent_id"], 2)

    @patch("pipeline_plugins.components.collections.sites.open.cc.create_set_by_template.v1_0.get_client_by_username")
    def test_execute_unknown_method(self, mock_get_client):
        parent_data = MagicMock()
        parent_data.get_one_of_inputs.return_value = None
        data = MagicMock()
        data.get_one_of_inputs.return_value = "unknown"

        result = self.service.execute(data, parent_data)
        self.assertFalse(result)
        data.set_outputs.assert_called_with("ex_data", "请选择填参方式")

    @patch("pipeline_plugins.components.collections.sites.open.cc.create_set_by_template.v1_0.cc_format_tree_mode_id")
    @patch("pipeline_plugins.components.collections.sites.open.cc.create_set_by_template.v1_0.get_client_by_username")
    def test_execute_create_fail(self, mock_get_client, mock_cc_format_tree_mode_id):
        # Prepare
        parent_data = MagicMock()
        parent_data.get_one_of_inputs.return_value = None
        data = MagicMock()
        data.get_one_of_inputs.side_effect = lambda key, default=None: {
            "biz_cc_id": "1",
            "cc_select_set_parent_method": "topo",
            "cc_set_parent_select_topo": [1],
            "cc_set_name": "set1",
            "cc_set_template": "100",
        }.get(key, default)

        mock_client = MagicMock()
        mock_client.api.create_set.return_value = {"result": False, "message": "error"}
        mock_get_client.return_value = mock_client
        mock_cc_format_tree_mode_id.return_value = [1]

        # Act
        result = self.service.execute(data, parent_data)

        # Assert
        self.assertFalse(result)
        data.set_outputs.assert_called()  # ex_data set

    @patch("pipeline_plugins.components.collections.sites.open.cc.create_set_by_template.v1_0.cc_format_tree_mode_id")
    @patch("pipeline_plugins.components.collections.sites.open.cc.create_set_by_template.v1_0.get_client_by_username")
    def test_execute_attr_capacity_fail(self, mock_get_client, mock_cc_format_tree_mode_id):
        # Prepare
        parent_data = MagicMock()
        parent_data.get_one_of_inputs.return_value = None
        data = MagicMock()
        data.get_one_of_inputs.side_effect = lambda key, default=None: {
            "biz_cc_id": "1",
            "cc_select_set_parent_method": "topo",
            "cc_set_parent_select_topo": [1],
            "cc_set_name": "set1",
            "cc_set_template": "100",
            "cc_set_attr": [{"attr_id": "bk_capacity", "attr_value": "not_int"}],
        }.get(key, default)

        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_cc_format_tree_mode_id.return_value = [1]

        # Act
        result = self.service.execute(data, parent_data)

        # Assert
        self.assertFalse(result)
        data.set_outputs.assert_called_with("ex_data", "集群容量必须为整数")

    @patch(
        "pipeline_plugins.components.collections.sites.open.cc.create_set_by_template.v1_0.cc_list_select_node_inst_id"
    )
    @patch("pipeline_plugins.components.collections.sites.open.cc.create_set_by_template.v1_0.get_client_by_username")
    def test_execute_text_fail(self, mock_get_client, mock_cc_list_select_node_inst_id):
        parent_data = MagicMock()
        parent_data.get_one_of_inputs.return_value = None
        data = MagicMock()
        data.get_one_of_inputs.side_effect = lambda key, default=None: {
            "cc_select_set_parent_method": "text",
            "cc_set_parent_select_text": "path",
        }.get(key, default)

        mock_cc_list_select_node_inst_id.return_value = {"result": False, "message": "error"}

        result = self.service.execute(data, parent_data)
        self.assertFalse(result)
        data.set_outputs.assert_called_with("ex_data", "error")
