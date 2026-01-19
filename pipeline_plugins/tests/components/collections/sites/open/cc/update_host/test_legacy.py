# -*- coding: utf-8 -*-
from django.test import TestCase
from mock import MagicMock, patch

from pipeline_plugins.components.collections.sites.open.cc.update_host.legacy import CCUpdateHostService


class CCUpdateHostServiceLegacyTestCase(TestCase):
    def setUp(self):
        self.service = CCUpdateHostService()
        self.service.logger = MagicMock()

    def test_inputs_format(self):
        inputs = self.service.inputs_format()
        self.assertIsInstance(inputs, list)
        self.assertEqual(len(inputs), 4)

    def test_outputs_format(self):
        outputs = self.service.outputs_format()
        self.assertIsInstance(outputs, list)
        self.assertEqual(len(outputs), 0)

    @patch("pipeline_plugins.components.collections.sites.open.cc.update_host.legacy.get_client_by_username")
    @patch("pipeline_plugins.components.collections.sites.open.cc.update_host.legacy.cc_format_prop_data")
    def test_execute_success(self, mock_format_prop, mock_get_client):
        # Mock inputs
        executor = "admin"
        tenant_id = "1"
        biz_cc_id = "2"
        cc_host_ip = "1.1.1.1"
        cc_host_property = "bk_isp_name"
        cc_host_prop_value = "1"

        data = MagicMock()
        data.get_one_of_inputs.side_effect = lambda key, default=None: {
            "biz_cc_id": biz_cc_id,
            "cc_host_ip": cc_host_ip,
            "cc_host_property": cc_host_property,
            "cc_host_prop_value": cc_host_prop_value,
        }.get(key, default)

        parent_data = MagicMock()
        parent_data.get_one_of_inputs.side_effect = lambda key: {
            "executor": executor,
            "tenant_id": tenant_id,
            "language": "zh-cn",
        }.get(key)
        parent_data.inputs.biz_cc_id = biz_cc_id

        # Mock helpers
        self.service.get_host_list_with_cloud_id = MagicMock(return_value={"result": True, "data": ["100"]})
        mock_format_prop.return_value = {"result": True, "data": {"1": "1"}}

        # Mock client
        client = MagicMock()
        mock_get_client.return_value = client
        client.api.search_object_attribute.return_value = {
            "result": True,
            "data": [{"bk_property_id": "bk_isp_name", "bk_property_type": "int"}],
        }
        client.api.update_host.return_value = {"result": True}

        # Execute
        result = self.service.execute(data, parent_data)

        # Assertions
        self.assertTrue(result)
        client.api.update_host.assert_called_once()
        call_args = client.api.update_host.call_args[0][0]
        self.assertEqual(call_args["bk_host_id"], "100")
        self.assertEqual(call_args["bk_isp_name"], 1)

    @patch("pipeline_plugins.components.collections.sites.open.cc.update_host.legacy.get_client_by_username")
    def test_execute_host_fail(self, mock_get_client):
        # Mock inputs
        executor = "admin"
        tenant_id = "1"
        biz_cc_id = "2"
        cc_host_ip = "1.1.1.1"

        data = MagicMock()
        data.get_one_of_inputs.side_effect = lambda key, default=None: {
            "biz_cc_id": biz_cc_id,
            "cc_host_ip": cc_host_ip,
        }.get(key, default)

        parent_data = MagicMock()
        parent_data.get_one_of_inputs.side_effect = lambda key: {
            "executor": executor,
            "tenant_id": tenant_id,
        }.get(key)
        parent_data.inputs.biz_cc_id = biz_cc_id

        # Mock helpers
        self.service.get_host_list_with_cloud_id = MagicMock(return_value={"result": False, "message": "host fail"})

        mock_get_client.return_value = MagicMock()

        # Execute
        result = self.service.execute(data, parent_data)

        # Assertions
        self.assertFalse(result)
        data.set_outputs.assert_called_with("ex_data", "host fail")

    @patch("pipeline_plugins.components.collections.sites.open.cc.update_host.legacy.get_client_by_username")
    @patch("pipeline_plugins.components.collections.sites.open.cc.update_host.legacy.cc_format_prop_data")
    def test_execute_isp_fail(self, mock_format_prop, mock_get_client):
        # Mock inputs
        executor = "admin"
        tenant_id = "1"
        biz_cc_id = "2"
        cc_host_ip = "1.1.1.1"
        cc_host_property = "bk_isp_name"
        cc_host_prop_value = "invalid"

        data = MagicMock()
        data.get_one_of_inputs.side_effect = lambda key, default=None: {
            "biz_cc_id": biz_cc_id,
            "cc_host_ip": cc_host_ip,
            "cc_host_property": cc_host_property,
            "cc_host_prop_value": cc_host_prop_value,
        }.get(key, default)

        parent_data = MagicMock()
        parent_data.get_one_of_inputs.side_effect = lambda key: {
            "executor": executor,
            "tenant_id": tenant_id,
        }.get(key)
        parent_data.inputs.biz_cc_id = biz_cc_id

        # Mock helpers
        self.service.get_host_list_with_cloud_id = MagicMock(return_value={"result": True, "data": ["100"]})
        mock_format_prop.return_value = {"result": True, "data": {"1": "1"}}

        mock_get_client.return_value = MagicMock()

        # Execute
        result = self.service.execute(data, parent_data)

        # Assertions
        self.assertFalse(result)
        data.set_outputs.assert_called_with("ex_data", "所属运营商校验失败，请重试并修改为正确的所属运营商")

    @patch("pipeline_plugins.components.collections.sites.open.cc.update_host.legacy.get_client_by_username")
    @patch("pipeline_plugins.components.collections.sites.open.cc.update_host.legacy.cc_format_prop_data")
    def test_execute_state_fail(self, mock_format_prop, mock_get_client):
        # Mock inputs
        executor = "admin"
        tenant_id = "1"
        biz_cc_id = "2"
        cc_host_ip = "1.1.1.1"
        cc_host_property = "bk_state_name"
        cc_host_prop_value = "invalid"

        data = MagicMock()
        data.get_one_of_inputs.side_effect = lambda key, default=None: {
            "biz_cc_id": biz_cc_id,
            "cc_host_ip": cc_host_ip,
            "cc_host_property": cc_host_property,
            "cc_host_prop_value": cc_host_prop_value,
        }.get(key, default)

        parent_data = MagicMock()
        parent_data.get_one_of_inputs.side_effect = lambda key: {
            "executor": executor,
            "tenant_id": tenant_id,
        }.get(key)
        parent_data.inputs.biz_cc_id = biz_cc_id

        # Mock helpers
        self.service.get_host_list_with_cloud_id = MagicMock(return_value={"result": True, "data": ["100"]})
        mock_format_prop.return_value = {"result": True, "data": {"1": "1"}}

        mock_get_client.return_value = MagicMock()

        # Execute
        result = self.service.execute(data, parent_data)

        # Assertions
        self.assertFalse(result)
        data.set_outputs.assert_called_with("ex_data", "所在国家校验失败，请重试并修改为正确的所在国家")

    @patch("pipeline_plugins.components.collections.sites.open.cc.update_host.legacy.get_client_by_username")
    @patch("pipeline_plugins.components.collections.sites.open.cc.update_host.legacy.cc_format_prop_data")
    def test_execute_province_fail(self, mock_format_prop, mock_get_client):
        # Mock inputs
        executor = "admin"
        tenant_id = "1"
        biz_cc_id = "2"
        cc_host_ip = "1.1.1.1"
        cc_host_property = "bk_province_name"
        cc_host_prop_value = "invalid"

        data = MagicMock()
        data.get_one_of_inputs.side_effect = lambda key, default=None: {
            "biz_cc_id": biz_cc_id,
            "cc_host_ip": cc_host_ip,
            "cc_host_property": cc_host_property,
            "cc_host_prop_value": cc_host_prop_value,
        }.get(key, default)

        parent_data = MagicMock()
        parent_data.get_one_of_inputs.side_effect = lambda key: {
            "executor": executor,
            "tenant_id": tenant_id,
        }.get(key)
        parent_data.inputs.biz_cc_id = biz_cc_id

        # Mock helpers
        self.service.get_host_list_with_cloud_id = MagicMock(return_value={"result": True, "data": ["100"]})
        mock_format_prop.return_value = {"result": True, "data": {"1": "1"}}

        mock_get_client.return_value = MagicMock()

        # Execute
        result = self.service.execute(data, parent_data)

        # Assertions
        self.assertFalse(result)
        data.set_outputs.assert_called_with("ex_data", "所在省份校验失败，请重试并修改为正确的所在省份")

    @patch("pipeline_plugins.components.collections.sites.open.cc.update_host.legacy.get_client_by_username")
    def test_execute_search_attr_fail(self, mock_get_client):
        # Mock inputs
        executor = "admin"
        tenant_id = "1"
        biz_cc_id = "2"
        cc_host_ip = "1.1.1.1"
        cc_host_property = "other"
        cc_host_prop_value = "val"

        data = MagicMock()
        data.get_one_of_inputs.side_effect = lambda key, default=None: {
            "biz_cc_id": biz_cc_id,
            "cc_host_ip": cc_host_ip,
            "cc_host_property": cc_host_property,
            "cc_host_prop_value": cc_host_prop_value,
        }.get(key, default)

        parent_data = MagicMock()
        parent_data.get_one_of_inputs.side_effect = lambda key: {
            "executor": executor,
            "tenant_id": tenant_id,
        }.get(key)
        parent_data.inputs.biz_cc_id = biz_cc_id

        # Mock helpers
        self.service.get_host_list_with_cloud_id = MagicMock(return_value={"result": True, "data": ["100"]})

        client = MagicMock()
        mock_get_client.return_value = client
        client.api.search_object_attribute.return_value = {"result": False, "message": "search attr fail"}

        # Execute
        result = self.service.execute(data, parent_data)

        # Assertions
        self.assertFalse(result)
        data.set_outputs.assert_called()
        args, _ = data.set_outputs.call_args
        self.assertEqual(args[0], "ex_data")
        self.assertIn("search attr fail", args[1])

    @patch("pipeline_plugins.components.collections.sites.open.cc.update_host.legacy.get_client_by_username")
    def test_execute_update_fail(self, mock_get_client):
        # Mock inputs
        executor = "admin"
        tenant_id = "1"
        biz_cc_id = "2"
        cc_host_ip = "1.1.1.1"
        cc_host_property = "other"
        cc_host_prop_value = "val"

        data = MagicMock()
        data.get_one_of_inputs.side_effect = lambda key, default=None: {
            "biz_cc_id": biz_cc_id,
            "cc_host_ip": cc_host_ip,
            "cc_host_property": cc_host_property,
            "cc_host_prop_value": cc_host_prop_value,
        }.get(key, default)

        parent_data = MagicMock()
        parent_data.get_one_of_inputs.side_effect = lambda key: {
            "executor": executor,
            "tenant_id": tenant_id,
        }.get(key)
        parent_data.inputs.biz_cc_id = biz_cc_id

        # Mock helpers
        self.service.get_host_list_with_cloud_id = MagicMock(return_value={"result": True, "data": ["100"]})

        client = MagicMock()
        mock_get_client.return_value = client
        client.api.search_object_attribute.return_value = {
            "result": True,
            "data": [{"bk_property_id": "other", "bk_property_type": "singlechar"}],
        }
        client.api.update_host.return_value = {"result": False, "message": "update fail"}

        # Execute
        result = self.service.execute(data, parent_data)

        # Assertions
        self.assertFalse(result)
        data.set_outputs.assert_called()
        args, _ = data.set_outputs.call_args
        self.assertEqual(args[0], "ex_data")
        self.assertIn("update fail", args[1])

    @patch("pipeline_plugins.components.collections.sites.open.cc.update_host.legacy.get_client_by_username")
    @patch("pipeline_plugins.components.collections.sites.open.cc.update_host.legacy.cc_format_prop_data")
    def test_execute_prop_data_fail(self, mock_format_prop, mock_get_client):
        # Mock inputs
        executor = "admin"
        tenant_id = "1"
        biz_cc_id = "2"
        cc_host_ip = "1.1.1.1"
        cc_host_property = "bk_isp_name"
        cc_host_prop_value = "1"

        data = MagicMock()
        data.get_one_of_inputs.side_effect = lambda key, default=None: {
            "biz_cc_id": biz_cc_id,
            "cc_host_ip": cc_host_ip,
            "cc_host_property": cc_host_property,
            "cc_host_prop_value": cc_host_prop_value,
        }.get(key, default)

        parent_data = MagicMock()
        parent_data.get_one_of_inputs.side_effect = lambda key: {
            "executor": executor,
            "tenant_id": tenant_id,
        }.get(key)
        parent_data.inputs.biz_cc_id = biz_cc_id

        # Mock helpers
        self.service.get_host_list_with_cloud_id = MagicMock(return_value={"result": True, "data": ["100"]})
        mock_format_prop.return_value = {"result": False, "message": "prop fail"}

        mock_get_client.return_value = MagicMock()

        # Execute
        result = self.service.execute(data, parent_data)

        # Assertions
        self.assertFalse(result)
        data.set_outputs.assert_called_with("ex_data", "prop fail")
