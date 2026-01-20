# -*- coding: utf-8 -*-
import json
from unittest.mock import MagicMock, patch

from django.http import HttpResponse, JsonResponse
from django.test import RequestFactory, TestCase

from gcloud.exceptions import ApiRequestError
from pipeline_plugins.base.query.cmdb import cc_get_host_by_module_id, cc_search_module
from pipeline_plugins.base.utils.adapter import cc_format_module_hosts, cc_get_inner_ip_by_module_id
from pipeline_plugins.base.utils.inject import (
    supplier_account_for_business,
    supplier_account_for_project,
    supplier_account_inject,
    supplier_id_for_business,
    supplier_id_for_project,
    supplier_id_inject,
)
from pipeline_plugins.middlewares import PluginApiRequestHandleMiddleware


class BaseSupplementTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    # --- pipeline_plugins/base/query/cmdb.py ---
    @patch("pipeline_plugins.base.query.cmdb.get_client_by_request")
    @patch("pipeline_plugins.base.query.cmdb.cc_format_module_hosts")
    def test_cc_get_host_by_module_id(self, mock_format, mock_get_client):
        # Setup mock
        client = MagicMock()
        mock_get_client.return_value = client
        mock_format.return_value = [{"host_id": 1}]

        # Test request with params
        request = self.factory.get("/", {"query": json.dumps(["1", "2"]), "host_fields": json.dumps(["inner_ip"])})
        request.user = MagicMock()
        request.user.username = "admin"
        request.user.tenant_id = "tenant"

        response = cc_get_host_by_module_id(request, "1")
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertTrue(content["result"])

        # Test without host_fields (default)
        request = self.factory.get("/", {"query": json.dumps(["1"])})
        request.user = MagicMock()
        request.user.username = "admin"
        request.user.tenant_id = "tenant"
        response = cc_get_host_by_module_id(request, "1")
        self.assertEqual(response.status_code, 200)

    @patch("pipeline_plugins.base.query.cmdb.get_client_by_request")
    def test_cc_search_module(self, mock_get_client):
        client = MagicMock()
        mock_get_client.return_value = client
        client.api.search_module.return_value = {"result": True, "data": {"info": [{"bk_module_id": 1}]}}

        # Valid request
        request = self.factory.get("/", {"bk_set_id": "1", "module_fields": json.dumps(["bk_module_name"])})
        request.user = MagicMock()
        request.user.username = "admin"
        request.user.tenant_id = "tenant"

        response = cc_search_module(request, "1")
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertTrue(content["result"])

        # Invalid bk_set_id (ValueError)
        request = self.factory.get("/", {"bk_set_id": "invalid"})
        request.user = MagicMock()
        response = cc_search_module(request, "1")
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertFalse(content["result"])

        # API fail
        client.api.search_module.return_value = {"result": False, "message": "error"}
        request = self.factory.get("/", {"bk_set_id": "1"})
        request.user = MagicMock()
        request.user.tenant_id = "tenant"
        response = cc_search_module(request, "1")
        self.assertFalse(json.loads(response.content)["result"])

    # --- pipeline_plugins/base/utils/adapter.py ---
    @patch("pipeline_plugins.base.utils.adapter.cmdb.get_business_host_topo")
    def test_cc_get_inner_ip_by_module_id(self, mock_get_topo):
        mock_get_topo.return_value = [
            {"host": {"bk_host_innerip": "1.1.1.1"}, "module": [{"bk_module_id": 1}]},
            {"host": {"bk_host_innerip": "2.2.2.2"}, "module": [{"bk_module_id": 2}]},
        ]

        # Match module 1
        result = cc_get_inner_ip_by_module_id("tenant", "user", "biz", [1], ["host"])
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["host"]["bk_host_innerip"], "1.1.1.1")

        # Match module 2
        result = cc_get_inner_ip_by_module_id("tenant", "user", "biz", [2], ["host"])
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["host"]["bk_host_innerip"], "2.2.2.2")

        # Match none
        result = cc_get_inner_ip_by_module_id("tenant", "user", "biz", [3], ["host"])
        self.assertEqual(len(result), 0)

    @patch("pipeline_plugins.base.utils.adapter.cc_get_inner_ip_by_module_id")
    def test_cc_format_module_hosts(self, mock_get_ip):
        mock_get_ip.return_value = [
            {"host": {"bk_host_innerip": "1.1.1.1"}, "module": [{"bk_module_id": 1, "bk_module_name": "mod1"}]}
        ]

        # Format tree
        result = cc_format_module_hosts("tenant", "user", "biz", [1], "tree", ["host"])
        self.assertEqual(len(result), 1)
        self.assertEqual(result["module_1"][0]["label"], "1.1.1.1")

        # Format ip (else)
        result = cc_format_module_hosts("tenant", "user", "biz", [1], "ip", ["host"])
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["host"]["bk_host_innerip"], "1.1.1.1")

    # --- pipeline_plugins/base/utils/inject.py ---
    @patch("pipeline_plugins.base.utils.inject.Project")
    @patch("pipeline_plugins.base.utils.inject.Business")
    def test_inject_functions(self, mock_biz, mock_proj):
        # Fix DoesNotExist
        mock_proj.DoesNotExist = Exception
        mock_biz.DoesNotExist = Exception

        # supplier_account_for_project
        # Case 1: Project not exist
        mock_proj.objects.get.side_effect = Exception("Not found")
        self.assertEqual(supplier_account_for_project(1), 0)

        # Case 2: from_cmdb=False
        mock_proj.objects.get.side_effect = None
        proj = MagicMock()
        proj.from_cmdb = False
        mock_proj.objects.get.return_value = proj
        self.assertEqual(supplier_account_for_project(1), 0)

        # Case 3: from_cmdb=True, call business
        proj.from_cmdb = True
        proj.bk_biz_id = 100
        mock_biz.objects.supplier_account_for_business.return_value = 123
        self.assertEqual(supplier_account_for_project(1), 123)

        # supplier_account_for_business
        # Case 1: Biz not exist
        mock_biz.objects.supplier_account_for_business.side_effect = Exception("Not found")
        self.assertEqual(supplier_account_for_business(100), 0)

    def test_inject_id_functions(self):
        with patch("pipeline_plugins.base.utils.inject.Project") as mock_proj, patch(
            "pipeline_plugins.base.utils.inject.Business"
        ) as mock_biz:

            mock_proj.DoesNotExist = Exception
            mock_biz.DoesNotExist = Exception

            # supplier_id_for_project
            # Case 1: Project not exist
            mock_proj.objects.get.side_effect = Exception("Not found")
            self.assertEqual(supplier_id_for_project(1), 0)

            # Case 2: from_cmdb=False
            mock_proj.objects.get.side_effect = None
            proj = MagicMock()
            proj.from_cmdb = False
            mock_proj.objects.get.return_value = proj
            self.assertEqual(supplier_id_for_project(1), 0)

            # Case 3: from_cmdb=True
            proj.from_cmdb = True
            proj.bk_biz_id = 100
            mock_biz.objects.supplier_id_for_business.return_value = 999
            self.assertEqual(supplier_id_for_project(1), 999)

            # supplier_id_for_business
            mock_biz.objects.supplier_id_for_business.side_effect = Exception("Not found")
            self.assertEqual(supplier_id_for_business(100), 0)

    def test_supplier_account_inject(self):
        @supplier_account_inject
        def my_func(*args, **kwargs):
            return kwargs.get("supplier_account")

        # No args
        self.assertIsNone(my_func())

        # project_id
        with patch("pipeline_plugins.base.utils.inject.supplier_account_for_project", return_value=10):
            self.assertEqual(my_func(project_id=1), 10)

        # biz_cc_id
        with patch("pipeline_plugins.base.utils.inject.supplier_account_for_business", return_value=20):
            self.assertEqual(my_func(biz_cc_id=1), 20)

        # bk_biz_id
        with patch("pipeline_plugins.base.utils.inject.supplier_account_for_business", return_value=30):
            self.assertEqual(my_func(bk_biz_id=1), 30)

    def test_supplier_id_inject(self):
        @supplier_id_inject
        def my_func(*args, **kwargs):
            return kwargs.get("supplier_id")

        # No args
        self.assertIsNone(my_func())

        # project_id
        with patch("pipeline_plugins.base.utils.inject.supplier_id_for_project", return_value=10):
            self.assertEqual(my_func(project_id=1), 10)

        # biz_cc_id
        with patch("pipeline_plugins.base.utils.inject.supplier_id_for_business", return_value=20):
            self.assertEqual(my_func(biz_cc_id=1), 20)

        # bk_biz_id
        with patch("pipeline_plugins.base.utils.inject.supplier_id_for_business", return_value=30):
            self.assertEqual(my_func(bk_biz_id=1), 30)

    # --- pipeline_plugins/middlewares.py ---
    def test_middleware(self):
        mw = PluginApiRequestHandleMiddleware(lambda r: HttpResponse())
        req = self.factory.get("/")

        # No exception
        self.assertIsNone(mw.process_exception(req, ValueError()))

        # ApiRequestError
        resp = mw.process_exception(req, ApiRequestError("test error"))
        self.assertIsInstance(resp, JsonResponse)
        content = json.loads(resp.content)
        self.assertFalse(content["result"])
        self.assertIn("test error", str(content["message"]))
