# -*- coding: utf-8 -*-
import json

from django.test import RequestFactory, TestCase
from mock import MagicMock, patch

from pipeline_plugins.components.query.sites.open.nodeman import (
    nodeman_get_ap_list,
    nodeman_get_cloud_area,
    nodeman_get_install_channel,
    nodeman_get_plugin_list,
    nodeman_get_plugin_version,
    nodeman_is_support_tjj,
)


class NodemanTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = MagicMock()
        self.user.username = "admin"
        self.user.tenant_id = "default"

    @patch("pipeline_plugins.components.query.sites.open.nodeman.get_client_by_username")
    def test_nodeman_get_cloud_area_success(self, mock_get_client):
        request = self.factory.get("/nodeman_get_cloud_area/")
        request.user = self.user

        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.api.cloud_list.return_value = {
            "result": True,
            "data": [{"bk_cloud_name": "Default Area", "bk_cloud_id": 0}],
            "code": 0,
            "message": "success",
        }

        response = nodeman_get_cloud_area(request)
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertTrue(content["result"])
        self.assertEqual(content["data"][0]["text"], "Default Area")
        self.assertEqual(content["data"][0]["value"], 0)

    @patch("pipeline_plugins.components.query.sites.open.nodeman.handle_api_error")
    @patch("pipeline_plugins.components.query.sites.open.nodeman.check_and_raise_raw_auth_fail_exception")
    @patch("pipeline_plugins.components.query.sites.open.nodeman.get_client_by_username")
    def test_nodeman_get_cloud_area_fail(self, mock_get_client, mock_check_auth, mock_handle_error):
        request = self.factory.get("/nodeman_get_cloud_area/")
        request.user = self.user

        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.api.cloud_list.return_value = {
            "result": False,
            "data": [],
            "code": 500,
            "message": "failed",
        }
        mock_handle_error.return_value = "API Error"

        response = nodeman_get_cloud_area(request)
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertFalse(content["result"])
        self.assertEqual(content["message"], "API Error")
        mock_check_auth.assert_called_once()

    @patch("pipeline_plugins.components.query.sites.open.nodeman.get_client_by_username")
    def test_nodeman_get_ap_list_success(self, mock_get_client):
        request = self.factory.get("/nodeman_get_ap_list/")
        request.user = self.user

        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.api.ap_list.return_value = {
            "result": True,
            "data": [{"name": "Default AP", "id": 1}],
            "code": 0,
            "message": "success",
        }

        response = nodeman_get_ap_list(request)
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertTrue(content["result"])
        self.assertEqual(content["data"][0]["text"], "Default AP")
        self.assertEqual(content["data"][0]["value"], 1)

    @patch("pipeline_plugins.components.query.sites.open.nodeman.handle_api_error")
    @patch("pipeline_plugins.components.query.sites.open.nodeman.get_client_by_username")
    def test_nodeman_get_ap_list_fail(self, mock_get_client, mock_handle_error):
        request = self.factory.get("/nodeman_get_ap_list/")
        request.user = self.user

        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.api.ap_list.return_value = {
            "result": False,
            "data": [],
            "code": 500,
            "message": "failed",
        }
        mock_handle_error.return_value = "API Error"

        response = nodeman_get_ap_list(request)
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertFalse(content["result"])
        self.assertEqual(content["message"], "API Error")

    @patch("pipeline_plugins.components.query.sites.open.nodeman.get_client_by_username")
    def test_nodeman_get_plugin_list_success(self, mock_get_client):
        request = self.factory.get("/nodeman_get_plugin_list/official/")
        request.user = self.user

        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.api.plugin_list.return_value = {
            "result": True,
            "data": {"list": [{"name": "gse_agent"}]},
            "code": 0,
            "message": "success",
        }

        response = nodeman_get_plugin_list(request, category="official")
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertTrue(content["result"])
        self.assertEqual(content["data"][0]["text"], "gse_agent")
        self.assertEqual(content["data"][0]["value"], "gse_agent")
        mock_client.api.plugin_list.assert_called_with(
            {"category": "official"}, headers={"X-Bk-Tenant-Id": self.user.tenant_id}
        )

    @patch("pipeline_plugins.components.query.sites.open.nodeman.handle_api_error")
    @patch("pipeline_plugins.components.query.sites.open.nodeman.check_and_raise_raw_auth_fail_exception")
    @patch("pipeline_plugins.components.query.sites.open.nodeman.get_client_by_username")
    def test_nodeman_get_plugin_list_fail(self, mock_get_client, mock_check_auth, mock_handle_error):
        request = self.factory.get("/nodeman_get_plugin_list/official/")
        request.user = self.user

        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.api.plugin_list.return_value = {
            "result": False,
            "data": [],
            "code": 500,
            "message": "failed",
        }
        mock_handle_error.return_value = "API Error"

        response = nodeman_get_plugin_list(request, category="official")
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertFalse(content["result"])
        self.assertEqual(content["message"], "API Error")

    @patch("pipeline_plugins.components.query.sites.open.nodeman.get_client_by_username")
    def test_nodeman_get_plugin_version_success(self, mock_get_client):
        request = self.factory.get("/nodeman_get_plugin_version/gse_agent/linux/")
        request.user = self.user

        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.api.list_packages.return_value = {
            "result": True,
            "data": [{"version": "1.0.0"}],
            "code": 0,
            "message": "success",
        }

        response = nodeman_get_plugin_version(request, plugin="gse_agent", os_type="linux")
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertTrue(content["result"])
        self.assertEqual(content["data"][0]["text"], "1.0.0")
        self.assertEqual(content["data"][0]["value"], "1.0.0")
        mock_client.api.list_packages.assert_called_with(
            {"os": "LINUX"}, headers={"X-Bk-Tenant-Id": self.user.tenant_id}, path_params={"process": "gse_agent"}
        )

    @patch("pipeline_plugins.components.query.sites.open.nodeman.handle_api_error")
    @patch("pipeline_plugins.components.query.sites.open.nodeman.check_and_raise_raw_auth_fail_exception")
    @patch("pipeline_plugins.components.query.sites.open.nodeman.get_client_by_username")
    def test_nodeman_get_plugin_version_fail(self, mock_get_client, mock_check_auth, mock_handle_error):
        request = self.factory.get("/nodeman_get_plugin_version/gse_agent/linux/")
        request.user = self.user

        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.api.list_packages.return_value = {
            "result": False,
            "data": [],
            "code": 500,
            "message": "failed",
        }
        mock_handle_error.return_value = "API Error"

        response = nodeman_get_plugin_version(request, plugin="gse_agent", os_type="linux")
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertFalse(content["result"])
        self.assertEqual(content["message"], "API Error")

    def test_nodeman_is_support_tjj(self):
        request = self.factory.get("/nodeman_is_support_tjj/")
        request.user = self.user

        # We can't easily mock the constant import without reloading, but we can check the return structure
        response = nodeman_is_support_tjj(request)
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertTrue(content["result"])
        self.assertIn("data", content)

    @patch("pipeline_plugins.components.query.sites.open.nodeman.get_client_by_username")
    def test_nodeman_get_install_channel_success(self, mock_get_client):
        request = self.factory.get("/nodeman_get_install_channel/0/")
        request.user = self.user

        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.api.install_channel_list.return_value = {
            "result": True,
            "data": [{"name": "channel1", "id": 1, "bk_cloud_id": 0}, {"name": "channel2", "id": 2, "bk_cloud_id": 1}],
            "code": 0,
            "message": "success",
        }

        response = nodeman_get_install_channel(request, cloud_id=0)
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertTrue(content["result"])
        # Should only return cloud_id=0
        self.assertEqual(len(content["data"]), 1)
        self.assertEqual(content["data"][0]["text"], "channel1")
        self.assertEqual(content["data"][0]["value"], 1)

    @patch("pipeline_plugins.components.query.sites.open.nodeman.handle_api_error")
    @patch("pipeline_plugins.components.query.sites.open.nodeman.check_and_raise_raw_auth_fail_exception")
    @patch("pipeline_plugins.components.query.sites.open.nodeman.get_client_by_username")
    def test_nodeman_get_install_channel_fail(self, mock_get_client, mock_check_auth, mock_handle_error):
        request = self.factory.get("/nodeman_get_install_channel/0/")
        request.user = self.user

        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.api.install_channel_list.return_value = {
            "result": False,
            "data": [],
            "code": 500,
            "message": "failed",
        }
        mock_handle_error.return_value = "API Error"

        response = nodeman_get_install_channel(request, cloud_id=0)
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertFalse(content["result"])
        self.assertEqual(content["message"], "API Error")
