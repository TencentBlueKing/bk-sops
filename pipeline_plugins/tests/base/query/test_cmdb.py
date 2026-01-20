# -*- coding: utf-8 -*-
import ujson as json
from django.test import TestCase
from mock import MagicMock, patch

from pipeline_plugins.base.query.cmdb import cc_get_host_by_module_id, cc_search_module


class CMDBQueryTestCase(TestCase):
    @patch("pipeline_plugins.base.query.cmdb.cc_format_module_hosts")
    def test_cc_get_host_by_module_id_success(self, mock_format_module_hosts):
        request = MagicMock()
        request.GET.get.side_effect = lambda key, default=None: {
            "query": json.dumps(["1", "2"]),
            "host_fields": json.dumps(["bk_host_id"]),
            "format": "tree",
        }.get(key, default)
        request.user.tenant_id = "tenant"
        request.user.username = "user"
        biz_cc_id = 1

        expected_hosts = {"module_1": []}
        mock_format_module_hosts.return_value = expected_hosts

        response = cc_get_host_by_module_id(request, biz_cc_id)

        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertTrue(content["result"])
        self.assertEqual(content["data"], expected_hosts)

        mock_format_module_hosts.assert_called_with("tenant", "user", biz_cc_id, [1, 2], "tree", ["bk_host_id"])

    @patch("pipeline_plugins.base.query.cmdb.get_client_by_request")
    @patch("pipeline_plugins.base.query.cmdb.EnvironmentVariables.objects.get_var")
    def test_cc_search_module_success(self, mock_get_var, mock_get_client):
        request = MagicMock()
        request.GET.get.side_effect = lambda key, default=None: {
            "bk_set_id": "10",
            "module_fields": json.dumps(["bk_module_name"]),
        }.get(key, default)
        request.user.tenant_id = "tenant"
        biz_cc_id = 1

        mock_get_var.return_value = "0"

        mock_client = MagicMock()
        mock_client.api.search_module.return_value = {"result": True, "data": {"info": []}, "message": "success"}
        mock_get_client.return_value = mock_client

        response = cc_search_module(request, biz_cc_id)

        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertTrue(content["result"])
        self.assertEqual(content["data"], {"info": []})

    @patch("pipeline_plugins.base.query.cmdb.get_client_by_request")
    @patch("pipeline_plugins.base.query.cmdb.EnvironmentVariables.objects.get_var")
    def test_cc_search_module_api_fail(self, mock_get_var, mock_get_client):
        request = MagicMock()
        request.GET.get.side_effect = lambda key, default=None: {
            "bk_set_id": "10",
            "module_fields": json.dumps([]),
        }.get(key, default)
        request.user.tenant_id = "tenant"
        biz_cc_id = 1

        mock_client = MagicMock()
        mock_client.api.search_module.return_value = {"result": False, "data": {}, "message": "error"}
        mock_get_client.return_value = mock_client

        response = cc_search_module(request, biz_cc_id)

        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertFalse(content["result"])
        self.assertEqual(content["message"], "error")

    def test_cc_search_module_invalid_param(self):
        request = MagicMock()
        request.GET.get.side_effect = lambda key, default=None: {
            "bk_set_id": "invalid",
        }.get(key, default)
        biz_cc_id = 1

        response = cc_search_module(request, biz_cc_id)

        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertFalse(content["result"])
        self.assertIn("校验失败", content["message"])
