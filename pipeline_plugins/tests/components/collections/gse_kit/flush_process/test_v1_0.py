# -*- coding: utf-8 -*-
from django.test import TestCase
from mock import MagicMock, patch

from pipeline_plugins.components.collections.gse_kit.flush_process.v1_0 import GsekitFlushProcessService


class GsekitFlushProcessServiceTestCase(TestCase):
    def setUp(self):
        self.service = GsekitFlushProcessService()
        self.service.logger = MagicMock()

    def test_inputs_format(self):
        self.assertEqual(self.service.inputs_format(), [])

    def test_outputs_format(self):
        self.assertEqual(self.service.outputs_format(), [])

    @patch("pipeline_plugins.components.collections.gse_kit.flush_process.v1_0.get_client_by_username")
    def test_execute_success(self, mock_get_client):
        # Prepare
        executor = "admin"
        bk_biz_id = "1"
        tenant_id = "tenant_1"

        parent_data = MagicMock()
        parent_data.get_one_of_inputs.side_effect = lambda key: {
            "executor": executor,
            "biz_cc_id": bk_biz_id,
            "tenant_id": tenant_id,
        }.get(key)

        mock_client = MagicMock()
        mock_client.api.flush_process.return_value = {"result": True, "data": {}, "message": "success"}
        mock_get_client.return_value = mock_client

        # Act
        result = self.service.execute(None, parent_data)

        # Assert
        self.assertTrue(result)
        mock_client.api.flush_process.assert_called_once_with(
            bk_biz_id, headers={"X-Bk-Tenant-Id": tenant_id}, path_params={"bk_biz_id": bk_biz_id}
        )

    @patch("pipeline_plugins.components.collections.gse_kit.flush_process.v1_0.handle_api_error")
    @patch("pipeline_plugins.components.collections.gse_kit.flush_process.v1_0.get_client_by_username")
    def test_execute_fail(self, mock_get_client, mock_handle_api_error):
        # Prepare
        executor = "admin"
        bk_biz_id = "1"
        tenant_id = "tenant_1"

        parent_data = MagicMock()
        parent_data.get_one_of_inputs.side_effect = lambda key: {
            "executor": executor,
            "biz_cc_id": bk_biz_id,
            "tenant_id": tenant_id,
        }.get(key)

        data = MagicMock()

        mock_client = MagicMock()
        mock_client.api.flush_process.return_value = {"result": False, "data": {}, "message": "error"}
        mock_get_client.return_value = mock_client

        mock_handle_api_error.return_value = "error message"

        # Act
        result = self.service.execute(data, parent_data)

        # Assert
        self.assertFalse(result)
        mock_handle_api_error.assert_called_once()
        data.set_outputs.assert_called_once_with("ex_data", "error message")
