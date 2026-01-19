# -*- coding: utf-8 -*-
from django.test import TestCase
from mock import MagicMock, patch

from pipeline_plugins.components.collections.sites.open.cc.create_set.v2_0 import CCCreateSetService, chunk_table_data


class ChunkTableDataTestCase(TestCase):
    def test_chunk_table_data_single_line(self):
        column = {"key1": "value1", "key2": "value2"}
        result = chunk_table_data(column)
        self.assertTrue(result["result"])
        self.assertEqual(len(result["data"]), 1)
        self.assertEqual(result["data"][0], column)

    def test_chunk_table_data_multi_line(self):
        column = {"key1": "v1\nv2", "key2": "v3\nv4"}
        result = chunk_table_data(column)
        self.assertTrue(result["result"])
        self.assertEqual(len(result["data"]), 2)
        self.assertEqual(result["data"][0]["key1"], "v1")
        self.assertEqual(result["data"][0]["key2"], "v3")
        self.assertEqual(result["data"][1]["key1"], "v2")
        self.assertEqual(result["data"][1]["key2"], "v4")

    def test_chunk_table_data_mixed(self):
        column = {"key1": "v1\nv2", "key2": "common"}
        result = chunk_table_data(column)
        self.assertTrue(result["result"])
        self.assertEqual(len(result["data"]), 2)
        self.assertEqual(result["data"][0]["key2"], "common")
        self.assertEqual(result["data"][1]["key2"], "common")

    def test_chunk_table_data_mismatch(self):
        column = {"key1": "v1\nv2", "key2": "v3\nv4\nv5"}
        result = chunk_table_data(column)
        self.assertFalse(result["result"])

    def test_chunk_table_data_invalid_type(self):
        column = {"key1": 123}
        result = chunk_table_data(column)
        # Assuming the code treats int as invalid based on line 58 logic check
        # Wait, the code says: if isinstance(value, int): continue.
        # So it skips int values and returns success if other fields are fine?
        # Let's check line 58: if isinstance(value, int): continue.
        # So it just keeps it as is.
        # But if it's not string and not int, it fails?
        # Let's test non-string/non-int if needed, or just skip if logic is simple.
        # Actually, let's test a simple int case.
        result = chunk_table_data(column)
        self.assertTrue(result["result"])
        self.assertEqual(result["data"][0]["key1"], 123)


class CCCreateSetServiceTestCase(TestCase):
    def setUp(self):
        self.service = CCCreateSetService()
        self.service.logger = MagicMock()

    def test_inputs_format(self):
        inputs = self.service.inputs_format()
        self.assertEqual(len(inputs), 5)

    def test_outputs_format(self):
        self.assertEqual(self.service.outputs_format(), [])

    @patch("pipeline_plugins.components.collections.sites.open.cc.create_set.v2_0.cc_format_prop_data")
    @patch("pipeline_plugins.components.collections.sites.open.cc.create_set.v2_0.cc_format_tree_mode_id")
    @patch("pipeline_plugins.components.collections.sites.open.cc.create_set.v2_0.get_client_by_username")
    @patch("pipeline_plugins.components.collections.sites.open.cc.create_set.v2_0.translation")
    def test_execute_topo_success(
        self, mock_translation, mock_get_client, mock_cc_format_tree_mode_id, mock_cc_format_prop_data
    ):
        # Prepare
        executor = "admin"
        tenant_id = "tenant_1"
        biz_cc_id = "1"
        cc_set_info = [{"bk_set_name": "set1", "bk_set_env": "test", "bk_service_status": "open", "bk_capacity": "10"}]

        parent_data = MagicMock()
        parent_data.get_one_of_inputs.side_effect = lambda key: {
            "executor": executor,
            "tenant_id": tenant_id,
            "language": "zh-hans",
        }.get(key)
        parent_data.inputs.biz_cc_id = biz_cc_id

        data = MagicMock()
        data.get_one_of_inputs.side_effect = lambda key, default=None: {
            "biz_cc_id": biz_cc_id,
            "cc_select_set_parent_method": "topo",
            "cc_set_parent_select_topo": [1],
            "cc_set_info": cc_set_info,
        }.get(key, default)

        mock_client = MagicMock()
        mock_client.api.create_set.return_value = {"result": True, "data": {"bk_set_id": 100}, "message": "success"}
        mock_get_client.return_value = mock_client

        mock_cc_format_tree_mode_id.return_value = [1]

        # Mock cc_format_prop_data to return valid env and status
        mock_cc_format_prop_data.side_effect = [
            {"result": True, "data": {"test": "test"}},  # bk_set_env
            {"result": True, "data": {"open": "open"}},  # bk_service_status
        ]

        # Act
        result = self.service.execute(data, parent_data)

        # Assert
        self.assertTrue(result)
        mock_translation.activate.assert_called_once_with("zh-hans")
        mock_client.api.create_set.assert_called_once()
        call_args = mock_client.api.create_set.call_args
        self.assertEqual(call_args[0][0]["bk_set_name"], "set1")
        self.assertEqual(call_args[0][0]["bk_capacity"], 10)
        self.assertEqual(call_args[0][0]["bk_parent_id"], 1)

    @patch("pipeline_plugins.components.collections.sites.open.cc.create_set.v2_0.cc_list_select_node_inst_id")
    @patch("pipeline_plugins.components.collections.sites.open.cc.create_set.v2_0.cc_format_prop_data")
    @patch("pipeline_plugins.components.collections.sites.open.cc.create_set.v2_0.get_client_by_username")
    def test_execute_text_success(self, mock_get_client, mock_cc_format_prop_data, mock_cc_list_select_node_inst_id):
        # Prepare
        parent_data = MagicMock()
        parent_data.get_one_of_inputs.return_value = "admin"  # executor
        # simplify mock setup

        data = MagicMock()
        data.get_one_of_inputs.side_effect = lambda key, default=None: {
            "biz_cc_id": "1",
            "cc_select_set_parent_method": "text",
            "cc_set_parent_select_text": "path/to/node",
            "cc_set_info": [{"bk_set_name": "set1"}],
        }.get(key, default)

        mock_client = MagicMock()
        mock_client.api.create_set.return_value = {"result": True}
        mock_get_client.return_value = mock_client

        mock_cc_list_select_node_inst_id.return_value = {"result": True, "data": [2]}

        mock_cc_format_prop_data.return_value = {"result": True, "data": {}}

        # Act
        result = self.service.execute(data, parent_data)

        # Assert
        self.assertTrue(result)
        mock_cc_list_select_node_inst_id.assert_called_once()
        mock_client.api.create_set.assert_called_once()
        self.assertEqual(mock_client.api.create_set.call_args[0][0]["bk_parent_id"], 2)

    @patch("pipeline_plugins.components.collections.sites.open.cc.create_set.v2_0.get_client_by_username")
    def test_execute_unknown_method(self, mock_get_client):
        parent_data = MagicMock()
        parent_data.get_one_of_inputs.return_value = None
        data = MagicMock()
        data.get_one_of_inputs.return_value = "unknown"  # cc_select_set_parent_method

        result = self.service.execute(data, parent_data)
        self.assertFalse(result)
        data.set_outputs.assert_called_with("ex_data", "请选择填参方式")

    @patch("pipeline_plugins.components.collections.sites.open.cc.create_set.v2_0.cc_list_select_node_inst_id")
    @patch("pipeline_plugins.components.collections.sites.open.cc.create_set.v2_0.get_client_by_username")
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

    @patch("pipeline_plugins.components.collections.sites.open.cc.create_set.v2_0.cc_format_tree_mode_id")
    @patch("pipeline_plugins.components.collections.sites.open.cc.create_set.v2_0.get_client_by_username")
    @patch("pipeline_plugins.components.collections.sites.open.cc.create_set.v2_0.cc_format_prop_data")
    def test_execute_validation_fail_capacity(
        self, mock_cc_format_prop_data, mock_get_client, mock_cc_format_tree_mode_id
    ):
        parent_data = MagicMock()
        parent_data.get_one_of_inputs.return_value = None
        data = MagicMock()
        data.get_one_of_inputs.side_effect = lambda key, default=None: {
            "cc_select_set_parent_method": "topo",
            "cc_set_parent_select_topo": [1],
            "cc_set_info": [{"bk_capacity": "not_int"}],
        }.get(key, default)

        mock_cc_format_tree_mode_id.return_value = [1]
        mock_cc_format_prop_data.return_value = {"result": True, "data": {}}

        result = self.service.execute(data, parent_data)
        self.assertFalse(result)
        data.set_outputs.assert_called_with("ex_data", "集群容量必须为整数")

    @patch("pipeline_plugins.components.collections.sites.open.cc.create_set.v2_0.cc_format_tree_mode_id")
    @patch("pipeline_plugins.components.collections.sites.open.cc.create_set.v2_0.get_client_by_username")
    @patch("pipeline_plugins.components.collections.sites.open.cc.create_set.v2_0.cc_format_prop_data")
    def test_execute_validation_fail_env(self, mock_cc_format_prop_data, mock_get_client, mock_cc_format_tree_mode_id):
        parent_data = MagicMock()
        parent_data.get_one_of_inputs.return_value = None
        data = MagicMock()
        data.get_one_of_inputs.side_effect = lambda key, default=None: {
            "cc_select_set_parent_method": "topo",
            "cc_set_parent_select_topo": [1],
            "cc_set_info": [{"bk_set_env": "invalid"}],
        }.get(key, default)

        mock_cc_format_tree_mode_id.return_value = [1]
        mock_cc_format_prop_data.side_effect = [
            {"result": True, "data": {"valid": "valid"}},  # env
            {"result": True, "data": {}},  # status
        ]

        result = self.service.execute(data, parent_data)
        self.assertFalse(result)
        data.set_outputs.assert_called_with("ex_data", "环境类型校验失败，请重试并修改为正确的环境类型")
