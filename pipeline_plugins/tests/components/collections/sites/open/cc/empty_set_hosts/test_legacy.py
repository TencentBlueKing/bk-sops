# -*- coding: utf-8 -*-
from django.test import TestCase
from mock import MagicMock, patch

from pipeline_plugins.components.collections.sites.open.cc.empty_set_hosts.legacy import CCEmptySetHostsService


class CCEmptySetHostsServiceTestCase(TestCase):
    def setUp(self):
        self.service = CCEmptySetHostsService()
        self.service.logger = MagicMock()

    def test_inputs_format(self):
        inputs = self.service.inputs_format()
        self.assertEqual(len(inputs), 2)

    def test_outputs_format(self):
        self.assertEqual(self.service.outputs_format(), [])

    @patch("pipeline_plugins.components.collections.sites.open.cc.empty_set_hosts.legacy.cc_format_tree_mode_id")
    @patch("pipeline_plugins.components.collections.sites.open.cc.empty_set_hosts.legacy.get_client_by_username")
    def test_execute_success(self, mock_get_client, mock_cc_format_tree_mode_id):
        # Prepare
        executor = "admin"
        tenant_id = "tenant_1"
        biz_cc_id = "1"
        cc_set_select = [1, 2]

        parent_data = MagicMock()
        parent_data.get_one_of_inputs.side_effect = lambda key: {
            "executor": executor,
            "tenant_id": tenant_id,
        }.get(key)
        parent_data.inputs.biz_cc_id = biz_cc_id

        data = MagicMock()
        data.get_one_of_inputs.side_effect = lambda key, default=None: {
            "biz_cc_id": biz_cc_id,
            "cc_set_select": cc_set_select,
        }.get(key, default)

        mock_client = MagicMock()
        mock_client.api.transfer_sethost_to_idle_module.return_value = {
            "result": True,
            "data": {},
            "message": "success",
        }
        mock_get_client.return_value = mock_client

        mock_cc_format_tree_mode_id.return_value = cc_set_select

        # Act
        result = self.service.execute(data, parent_data)

        # Assert
        self.assertTrue(result)
        self.assertEqual(mock_client.api.transfer_sethost_to_idle_module.call_count, 2)

        call_args_list = mock_client.api.transfer_sethost_to_idle_module.call_args_list
        self.assertEqual(call_args_list[0][0][0]["bk_set_id"], 1)
        self.assertEqual(call_args_list[1][0][0]["bk_set_id"], 2)

    @patch("pipeline_plugins.components.collections.sites.open.cc.empty_set_hosts.legacy.cc_handle_api_error")
    @patch("pipeline_plugins.components.collections.sites.open.cc.empty_set_hosts.legacy.cc_format_tree_mode_id")
    @patch("pipeline_plugins.components.collections.sites.open.cc.empty_set_hosts.legacy.get_client_by_username")
    def test_execute_fail(self, mock_get_client, mock_cc_format_tree_mode_id, mock_cc_handle_api_error):
        # Prepare
        parent_data = MagicMock()
        parent_data.get_one_of_inputs.return_value = None

        data = MagicMock()
        data.get_one_of_inputs.side_effect = lambda key, default=None: {"biz_cc_id": "1", "cc_set_select": [1]}.get(
            key, default
        )

        mock_client = MagicMock()
        mock_client.api.transfer_sethost_to_idle_module.return_value = {"result": False, "message": "error"}
        mock_get_client.return_value = mock_client

        mock_cc_format_tree_mode_id.return_value = [1]
        mock_cc_handle_api_error.return_value = "error message"

        # Act
        result = self.service.execute(data, parent_data)

        # Assert
        self.assertFalse(result)
        mock_cc_handle_api_error.assert_called_once()
        data.set_outputs.assert_called_with("ex_data", "error message")
