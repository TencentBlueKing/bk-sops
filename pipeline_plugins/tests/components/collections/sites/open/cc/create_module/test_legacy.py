# -*- coding: utf-8 -*-
from django.test import TestCase
from mock import MagicMock, patch

from pipeline_plugins.components.collections.sites.open.cc.create_module.legacy import CCCreateModuleService


class CCCreateModuleServiceTestCase(TestCase):
    def setUp(self):
        self.service = CCCreateModuleService()
        self.service.logger = MagicMock()

    def test_inputs_format(self):
        inputs = self.service.inputs_format()
        self.assertEqual(len(inputs), 7)

    def test_outputs_format(self):
        self.assertEqual(self.service.outputs_format(), [])

    @patch("pipeline_plugins.components.collections.sites.open.cc.create_module.legacy.cc_format_tree_set_id")
    @patch("pipeline_plugins.components.collections.sites.open.cc.create_module.legacy.get_client_by_username")
    @patch(
        "pipeline_plugins.components.collections.sites.open.cc.create_module.legacy.cc_get_name_id_from_combine_value"
    )
    def test_execute_template_success(self, mock_get_name_id, mock_get_client, mock_cc_format_tree_set_id):
        # Prepare
        executor = "admin"
        tenant_id = "tenant_1"
        biz_cc_id = "1"

        parent_data = MagicMock()
        parent_data.get_one_of_inputs.side_effect = lambda key: {
            "executor": executor,
            "tenant_id": tenant_id,
        }.get(key)
        parent_data.inputs.biz_cc_id = biz_cc_id

        data = MagicMock()
        data.get_one_of_inputs.side_effect = lambda key, default=None: {
            "biz_cc_id": biz_cc_id,
            "cc_set_select_method": "topo",
            "cc_create_method": "template",
            "cc_set_select_topo": [1],
            "cc_module_infos_template": [{"cc_service_template": "template_1"}],
        }.get(key, default)

        mock_client = MagicMock()
        mock_client.api.create_module.return_value = {"result": True, "data": {}, "message": "success"}
        mock_get_client.return_value = mock_client

        mock_cc_format_tree_set_id.return_value = [1]
        mock_get_name_id.return_value = ("template_1", 100)

        # Act
        result = self.service.execute(data, parent_data)

        # Assert
        self.assertTrue(result)
        mock_client.api.create_module.assert_called_once()
        self.assertEqual(mock_client.api.create_module.call_args[0][0]["service_template_id"], 100)
        self.assertEqual(mock_client.api.create_module.call_args[0][0]["bk_module_name"], "template_1")

    @patch("pipeline_plugins.components.collections.sites.open.cc.create_module.legacy.cc_format_tree_set_id")
    @patch("pipeline_plugins.components.collections.sites.open.cc.create_module.legacy.get_client_by_username")
    @patch("pipeline_plugins.components.collections.sites.open.cc.create_module.legacy.cc_format_prop_data")
    def test_execute_category_success(self, mock_cc_format_prop_data, mock_get_client, mock_cc_format_tree_set_id):
        # Prepare
        parent_data = MagicMock()
        parent_data.get_one_of_inputs.side_effect = lambda key: {
            "executor": "admin",
            "tenant_id": "tenant_1",
            "language": "zh-hans",
        }.get(key)

        data = MagicMock()
        data.get_one_of_inputs.side_effect = lambda key, default=None: {
            "biz_cc_id": "1",
            "cc_set_select_method": "topo",
            "cc_create_method": "category",
            "cc_set_select_topo": [1],
            "cc_module_infos_category": [
                {"cc_service_category": [1, 2], "bk_module_name": "module_1", "bk_module_type": "type_1"}
            ],
        }.get(key, default)

        mock_client = MagicMock()
        mock_client.api.create_module.return_value = {"result": True, "data": {}}
        mock_get_client.return_value = mock_client

        mock_cc_format_tree_set_id.return_value = [1]
        mock_cc_format_prop_data.return_value = {"result": True, "data": {"type_1": "type_1"}}

        # Act
        result = self.service.execute(data, parent_data)

        # Assert
        self.assertTrue(result)
        mock_client.api.create_module.assert_called_once()
        self.assertEqual(mock_client.api.create_module.call_args[0][0]["service_category_id"], 2)
        self.assertEqual(mock_client.api.create_module.call_args[0][0]["bk_module_name"], "module_1")

    @patch("pipeline_plugins.components.collections.sites.open.cc.create_module.legacy.get_client_by_username")
    def test_execute_invalid_method(self, mock_get_client):
        parent_data = MagicMock()
        parent_data.get_one_of_inputs.return_value = None
        data = MagicMock()
        data.get_one_of_inputs.side_effect = lambda key, default=None: {
            "cc_set_select_method": "invalid",
        }.get(key, default)

        result = self.service.execute(data, parent_data)
        self.assertFalse(result)
        data.set_outputs.assert_called_with("ex_data", "请选择填参方式")

    @patch("pipeline_plugins.components.collections.sites.open.cc.create_module.legacy.cc_list_select_node_inst_id")
    @patch("pipeline_plugins.components.collections.sites.open.cc.create_module.legacy.get_client_by_username")
    def test_execute_text_fail(self, mock_get_client, mock_cc_list_select_node_inst_id):
        parent_data = MagicMock()
        parent_data.get_one_of_inputs.return_value = None
        data = MagicMock()
        data.get_one_of_inputs.side_effect = lambda key, default=None: {
            "cc_set_select_method": "text",
            "cc_create_method": "template",
            "cc_set_select_text": "path",
        }.get(key, default)

        mock_cc_list_select_node_inst_id.return_value = {"result": False, "message": "error"}

        result = self.service.execute(data, parent_data)
        self.assertFalse(result)
        data.set_outputs.assert_called_with("ex_data", "error")

    @patch("pipeline_plugins.components.collections.sites.open.cc.create_module.legacy.cc_format_tree_set_id")
    @patch("pipeline_plugins.components.collections.sites.open.cc.create_module.legacy.get_client_by_username")
    def test_execute_empty_modules(self, mock_get_client, mock_cc_format_tree_set_id):
        parent_data = MagicMock()
        parent_data.get_one_of_inputs.return_value = None
        data = MagicMock()
        data.get_one_of_inputs.side_effect = lambda key, default=None: {
            "cc_set_select_method": "topo",
            "cc_create_method": "template",
            "cc_set_select_topo": [1],
            "cc_module_infos_template": [],
        }.get(key, default)

        mock_cc_format_tree_set_id.return_value = [1]

        result = self.service.execute(data, parent_data)
        self.assertFalse(result)
        data.set_outputs.assert_called_with("ex_data", "模块信息不能为空")

    @patch("pipeline_plugins.components.collections.sites.open.cc.create_module.legacy.cc_format_tree_set_id")
    @patch("pipeline_plugins.components.collections.sites.open.cc.create_module.legacy.get_client_by_username")
    @patch(
        "pipeline_plugins.components.collections.sites.open.cc.create_module.legacy.cc_get_name_id_from_combine_value"
    )
    def test_execute_invalid_template(self, mock_get_name_id, mock_get_client, mock_cc_format_tree_set_id):
        parent_data = MagicMock()
        parent_data.get_one_of_inputs.return_value = None
        data = MagicMock()
        data.get_one_of_inputs.side_effect = lambda key, default=None: {
            "cc_set_select_method": "topo",
            "cc_create_method": "template",
            "cc_set_select_topo": [1],
            "cc_module_infos_template": [{"cc_service_template": "invalid"}],
        }.get(key, default)

        mock_cc_format_tree_set_id.return_value = [1]
        mock_get_name_id.return_value = (None, None)

        result = self.service.execute(data, parent_data)
        self.assertFalse(result)
        data.set_outputs.assert_called_with("ex_data", "请选择正确的服务模板")

    @patch("pipeline_plugins.components.collections.sites.open.cc.create_module.legacy.cc_format_tree_set_id")
    @patch("pipeline_plugins.components.collections.sites.open.cc.create_module.legacy.get_client_by_username")
    def test_execute_category_invalid_service_type(self, mock_get_client, mock_cc_format_tree_set_id):
        parent_data = MagicMock()
        parent_data.get_one_of_inputs.return_value = None
        data = MagicMock()
        data.get_one_of_inputs.side_effect = lambda key, default=None: {
            "cc_set_select_method": "topo",
            "cc_create_method": "category",
            "cc_set_select_topo": [1],
            "cc_module_infos_category": [{"cc_service_category": [1]}],  # Invalid length
        }.get(key, default)

        mock_cc_format_tree_set_id.return_value = [1]

        result = self.service.execute(data, parent_data)
        self.assertFalse(result)
        data.set_outputs.assert_called_with("ex_data", "请选择正确的服务类型")

    @patch("pipeline_plugins.components.collections.sites.open.cc.create_module.legacy.cc_format_tree_set_id")
    @patch("pipeline_plugins.components.collections.sites.open.cc.create_module.legacy.get_client_by_username")
    @patch("pipeline_plugins.components.collections.sites.open.cc.create_module.legacy.translation")
    def test_execute_language_setting(self, mock_translation, mock_get_client, mock_cc_format_tree_set_id):
        parent_data = MagicMock()
        parent_data.get_one_of_inputs.side_effect = lambda key: {
            "executor": "admin",
            "tenant_id": "tenant_1",
            "language": "en",
        }.get(key)

        data = MagicMock()
        data.get_one_of_inputs.side_effect = lambda key, default=None: {
            "biz_cc_id": "1",
            "cc_set_select_method": "topo",
            "cc_create_method": "template",
            "cc_set_select_topo": [1],
            "cc_module_infos_template": [],  # Empty to stop early
        }.get(key, default)

        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_cc_format_tree_set_id.return_value = [1]

        result = self.service.execute(data, parent_data)

        # We expect False because of empty modules, but we want to verify language activation
        self.assertFalse(result)
        mock_translation.activate.assert_called_once_with("en")
        self.assertEqual(mock_client.language, "en")

    @patch("pipeline_plugins.components.collections.sites.open.cc.create_module.legacy.get_client_by_username")
    def test_execute_invalid_create_method(self, mock_get_client):
        parent_data = MagicMock()
        parent_data.get_one_of_inputs.return_value = None
        data = MagicMock()
        data.get_one_of_inputs.side_effect = lambda key, default=None: {
            "cc_set_select_method": "topo",
            "cc_create_method": "invalid",
        }.get(key, default)

        result = self.service.execute(data, parent_data)
        self.assertFalse(result)
        data.set_outputs.assert_called_with("ex_data", "请选择创建方式")

    @patch("pipeline_plugins.components.collections.sites.open.cc.create_module.legacy.cc_format_tree_set_id")
    @patch("pipeline_plugins.components.collections.sites.open.cc.create_module.legacy.get_client_by_username")
    def test_execute_category_missing_module_name(self, mock_get_client, mock_cc_format_tree_set_id):
        parent_data = MagicMock()
        parent_data.get_one_of_inputs.return_value = None
        data = MagicMock()
        data.get_one_of_inputs.side_effect = lambda key, default=None: {
            "cc_set_select_method": "topo",
            "cc_create_method": "category",
            "cc_set_select_topo": [1],
            "cc_module_infos_category": [{"cc_service_category": [1, 2]}],  # Missing module name
        }.get(key, default)

        mock_cc_format_tree_set_id.return_value = [1]

        result = self.service.execute(data, parent_data)
        self.assertFalse(result)
        data.set_outputs.assert_called_with("ex_data", "模块名称不能为空")

    @patch("pipeline_plugins.components.collections.sites.open.cc.create_module.legacy.cc_format_tree_set_id")
    @patch("pipeline_plugins.components.collections.sites.open.cc.create_module.legacy.get_client_by_username")
    @patch("pipeline_plugins.components.collections.sites.open.cc.create_module.legacy.cc_format_prop_data")
    def test_execute_category_prop_data_fail(
        self, mock_cc_format_prop_data, mock_get_client, mock_cc_format_tree_set_id
    ):
        parent_data = MagicMock()
        parent_data.get_one_of_inputs.return_value = None
        data = MagicMock()
        data.get_one_of_inputs.side_effect = lambda key, default=None: {
            "cc_set_select_method": "topo",
            "cc_create_method": "category",
            "cc_set_select_topo": [1],
            "cc_module_infos_category": [
                {"cc_service_category": [1, 2], "bk_module_name": "module_1", "bk_module_type": "type_1"}
            ],
        }.get(key, default)

        mock_cc_format_tree_set_id.return_value = [1]
        mock_cc_format_prop_data.return_value = {"result": False, "message": "error"}

        result = self.service.execute(data, parent_data)
        self.assertFalse(result)
        data.set_outputs.assert_called_with("ex_data", "error")

    @patch("pipeline_plugins.components.collections.sites.open.cc.create_module.legacy.cc_format_tree_set_id")
    @patch("pipeline_plugins.components.collections.sites.open.cc.create_module.legacy.get_client_by_username")
    @patch("pipeline_plugins.components.collections.sites.open.cc.create_module.legacy.cc_format_prop_data")
    def test_execute_category_invalid_module_type(
        self, mock_cc_format_prop_data, mock_get_client, mock_cc_format_tree_set_id
    ):
        parent_data = MagicMock()
        parent_data.get_one_of_inputs.return_value = None
        data = MagicMock()
        data.get_one_of_inputs.side_effect = lambda key, default=None: {
            "cc_set_select_method": "topo",
            "cc_create_method": "category",
            "cc_set_select_topo": [1],
            "cc_module_infos_category": [
                {"cc_service_category": [1, 2], "bk_module_name": "module_1", "bk_module_type": "type_1"}
            ],
        }.get(key, default)

        mock_cc_format_tree_set_id.return_value = [1]
        mock_cc_format_prop_data.return_value = {"result": True, "data": {"type_2": "type_2"}}

        result = self.service.execute(data, parent_data)
        self.assertFalse(result)
        data.set_outputs.assert_called_with("ex_data", "模块类型校验失败，请重试并填写正确的模块类型")

    @patch("pipeline_plugins.components.collections.sites.open.cc.create_module.legacy.cc_format_tree_set_id")
    @patch("pipeline_plugins.components.collections.sites.open.cc.create_module.legacy.get_client_by_username")
    @patch(
        "pipeline_plugins.components.collections.sites.open.cc.create_module.legacy.cc_get_name_id_from_combine_value"
    )
    @patch("pipeline_plugins.components.collections.sites.open.cc.create_module.legacy.cc_handle_api_error")
    def test_execute_create_api_fail(
        self, mock_handle_api_error, mock_get_name_id, mock_get_client, mock_cc_format_tree_set_id
    ):
        parent_data = MagicMock()
        parent_data.get_one_of_inputs.return_value = None
        data = MagicMock()
        data.get_one_of_inputs.side_effect = lambda key, default=None: {
            "biz_cc_id": "1",
            "cc_set_select_method": "topo",
            "cc_create_method": "template",
            "cc_set_select_topo": [1],
            "cc_module_infos_template": [{"cc_service_template": "template_1"}],
        }.get(key, default)

        mock_client = MagicMock()
        mock_client.api.create_module.return_value = {"result": False, "message": "error"}
        mock_get_client.return_value = mock_client

        mock_cc_format_tree_set_id.return_value = [1]
        mock_get_name_id.return_value = ("template_1", 100)
        mock_handle_api_error.return_value = "api error"

        result = self.service.execute(data, parent_data)
        self.assertFalse(result)
        data.set_outputs.assert_called_with("ex_data", "api error")
