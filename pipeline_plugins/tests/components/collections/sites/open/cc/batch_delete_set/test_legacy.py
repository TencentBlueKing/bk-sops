# -*- coding: utf-8 -*-
from django.test import TestCase
from mock import MagicMock, patch

from pipeline_plugins.components.collections.sites.open.cc.batch_delete_set.legacy import CCBatchDeleteSetService


class CCBatchDeleteSetServiceTestCase(TestCase):
    def setUp(self):
        self.service = CCBatchDeleteSetService()
        self.service.logger = MagicMock()

    def test_inputs_format(self):
        inputs = self.service.inputs_format()
        self.assertEqual(len(inputs), 2)
        self.assertEqual(inputs[0].key, "biz_cc_id")
        self.assertEqual(inputs[1].key, "cc_set_select")

    def test_outputs_format(self):
        self.assertEqual(self.service.outputs_format(), [])

    @patch("pipeline_plugins.components.collections.sites.open.cc.batch_delete_set.legacy.cc_format_tree_mode_id")
    @patch("pipeline_plugins.components.collections.sites.open.cc.batch_delete_set.legacy.get_client_by_username")
    @patch("pipeline_plugins.components.collections.sites.open.cc.batch_delete_set.legacy.translation")
    def test_execute_success(self, mock_translation, mock_get_client, mock_cc_format_tree_mode_id):
        # Prepare
        executor = "admin"
        tenant_id = "tenant_1"
        biz_cc_id = "1"
        cc_set_select = [1, 2]
        language = "zh-hans"

        parent_data = MagicMock()
        parent_data.get_one_of_inputs.side_effect = lambda key: {
            "executor": executor,
            "tenant_id": tenant_id,
            "language": language,
        }.get(key)
        parent_data.inputs.biz_cc_id = biz_cc_id

        data = MagicMock()
        data.get_one_of_inputs.side_effect = lambda key, default=None: {
            "biz_cc_id": biz_cc_id,
            "cc_set_select": cc_set_select,
        }.get(key, default)

        mock_client = MagicMock()
        mock_client.api.batch_delete_set.return_value = {"result": True, "data": {}, "message": "success"}
        mock_get_client.return_value = mock_client

        mock_cc_format_tree_mode_id.return_value = cc_set_select

        # Act
        result = self.service.execute(data, parent_data)

        # Assert
        self.assertTrue(result)
        mock_translation.activate.assert_called_once_with(language)
        mock_client.api.batch_delete_set.assert_called_once()

        # Verify kwargs
        call_args = mock_client.api.batch_delete_set.call_args
        self.assertEqual(call_args[0][0]["bk_biz_id"], biz_cc_id)
        self.assertEqual(call_args[0][0]["delete"]["inst_ids"], cc_set_select)

    @patch("pipeline_plugins.components.collections.sites.open.cc.batch_delete_set.legacy.cc_handle_api_error")
    @patch("pipeline_plugins.components.collections.sites.open.cc.batch_delete_set.legacy.cc_format_tree_mode_id")
    @patch("pipeline_plugins.components.collections.sites.open.cc.batch_delete_set.legacy.get_client_by_username")
    def test_execute_fail(self, mock_get_client, mock_cc_format_tree_mode_id, mock_cc_handle_api_error):
        # Prepare
        executor = "admin"
        tenant_id = "tenant_1"
        biz_cc_id = "1"
        cc_set_select = [1, 2]

        parent_data = MagicMock()
        parent_data.get_one_of_inputs.side_effect = lambda key: {
            "executor": executor,
            "tenant_id": tenant_id,
            "language": None,
        }.get(key)
        parent_data.inputs.biz_cc_id = biz_cc_id

        data = MagicMock()
        data.get_one_of_inputs.side_effect = lambda key, default=None: {
            "biz_cc_id": biz_cc_id,
            "cc_set_select": cc_set_select,
        }.get(key, default)

        mock_client = MagicMock()
        mock_client.api.batch_delete_set.return_value = {"result": False, "data": {}, "message": "error"}
        mock_get_client.return_value = mock_client

        mock_cc_format_tree_mode_id.return_value = cc_set_select
        mock_cc_handle_api_error.return_value = "error message"

        # Act
        result = self.service.execute(data, parent_data)

        # Assert
        self.assertFalse(result)
        mock_cc_handle_api_error.assert_called_once()
        data.set_outputs.assert_called_once_with("ex_data", "error message")
