# -*- coding: utf-8 -*-
import json

from django.test import RequestFactory, TestCase
from mock import MagicMock, patch

from pipeline_plugins.variables.query.sites.open.query import (
    cc_get_module,
    cc_get_set,
    cc_get_set_attribute,
    cc_get_set_env,
    cc_get_set_group,
    cc_get_set_list,
    cc_list_service_template,
    get_staff_groups,
)
from pipeline_plugins.variables.query.sites.open.select import variable_select_source_data_proxy


class QueryTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = MagicMock()
        self.user.username = "admin"
        self.user.tenant_id = "default"
        self.biz_cc_id = 1
        self.biz_set_id = 10

    @patch("pipeline_plugins.variables.query.sites.open.query.get_client_by_username")
    @patch("pipeline_plugins.variables.query.sites.open.query.batch_request")
    @patch("pipeline_plugins.variables.query.sites.open.query.EnvironmentVariables.objects.get_var")
    def test_cc_get_set(self, mock_get_var, mock_batch, mock_get_client):
        request = self.factory.get("/cc_get_set/1/")
        request.user = self.user

        mock_batch.return_value = [{"bk_set_id": 10, "bk_set_name": "Set 1"}]
        mock_get_var.return_value = "0"

        response = cc_get_set(request, self.biz_cc_id)
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertTrue(content["result"])
        self.assertEqual(content["data"][0]["text"], "Set 1")
        self.assertEqual(content["data"][0]["value"], 10)

    @patch("pipeline_plugins.variables.query.sites.open.query.get_client_by_username")
    @patch("pipeline_plugins.variables.query.sites.open.query.batch_request")
    @patch("pipeline_plugins.variables.query.sites.open.query.EnvironmentVariables.objects.get_var")
    def test_cc_get_module(self, mock_get_var, mock_batch, mock_get_client):
        request = self.factory.get("/cc_get_module/1/10/")
        request.user = self.user

        mock_batch.return_value = [{"bk_module_id": 100, "bk_module_name": "Module 1"}]
        mock_get_var.return_value = "0"

        response = cc_get_module(request, self.biz_cc_id, self.biz_set_id)
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertTrue(content["result"])
        self.assertEqual(content["data"][0]["text"], "Module 1")
        self.assertEqual(content["data"][0]["value"], 100)

    @patch("pipeline_plugins.variables.query.sites.open.query.StaffGroupSet.objects.filter")
    def test_get_staff_groups(self, mock_filter):
        request = self.factory.get("/get_staff_groups/1/")
        request.user = self.user

        mock_qs = MagicMock()
        mock_qs.values.return_value = [{"id": 1, "name": "Group 1"}]
        mock_filter.return_value = mock_qs

        response = get_staff_groups(request, project_id=1)
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertTrue(content["result"])
        self.assertEqual(content["data"][0]["text"], "Group 1")

    @patch("pipeline_plugins.variables.query.sites.open.query.get_set_list")
    def test_cc_get_set_list(self, mock_get_list):
        request = self.factory.get("/cc_get_set_list/1/")
        request.user = self.user

        mock_get_list.return_value = [{"bk_set_name": "Set 1"}, {"bk_set_name": "Set 1"}]  # Duplicate to test dedupe

        response = cc_get_set_list(request, self.biz_cc_id)
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertTrue(content["result"])
        # First item is "all"
        self.assertEqual(content["data"][0]["value"], "all")
        # Should be deduped
        self.assertEqual(len(content["data"]), 2)
        self.assertEqual(content["data"][1]["text"], "Set 1")

    @patch("pipeline_plugins.variables.query.sites.open.query.get_biz_internal_module")
    @patch("pipeline_plugins.variables.query.sites.open.query.get_service_template_list")
    def test_cc_list_service_template(self, mock_get_templates, mock_get_internal):
        request = self.factory.get("/cc_get_service_template_list/1/")
        request.user = self.user

        mock_get_internal.return_value = {"data": [{"name": "idle"}]}
        mock_get_templates.return_value = [
            {"name": "Template 1"},
            {"name": "idle"},
        ]  # "idle" should be filtered out from templates list

        response = cc_list_service_template(request, self.biz_cc_id)
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertTrue(content["result"])

        # Check template
        self.assertEqual(content["data"][0]["text"], "Template 1")
        # Check internal module appended
        self.assertEqual(content["data"][-1]["text"], "idle")

    @patch("pipeline_plugins.variables.query.sites.open.query.get_client_by_username")
    @patch("pipeline_plugins.variables.query.sites.open.query.batch_request")
    def test_cc_get_set_group(self, mock_batch, mock_get_client):
        request = self.factory.get("/cc_get_set_group/1/")
        request.user = self.user

        mock_batch.return_value = [{"id": "grp1", "name": "Group 1"}]

        response = cc_get_set_group(request, self.biz_cc_id)
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertTrue(content["result"])
        self.assertEqual(content["data"][0]["text"], "Group 1")

    @patch("pipeline_plugins.variables.query.sites.open.query.get_client_by_username")
    def test_cc_get_set_attribute(self, mock_get_client):
        request = self.factory.get("/cc_get_set_attributes/1/")
        request.user = self.user

        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.api.search_object_attribute.return_value = {
            "result": True,
            "data": [{"bk_property_id": "prop1", "bk_property_name": "Prop 1"}],
        }

        response = cc_get_set_attribute(request, self.biz_cc_id)
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertTrue(content["result"])
        self.assertEqual(content["data"][0]["text"], "Prop 1")

    @patch("pipeline_plugins.variables.query.sites.open.query.get_client_by_username")
    def test_cc_get_set_env(self, mock_get_client):
        request = self.factory.get("/cc_get_set_env/obj/1/")
        request.user = self.user

        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.api.search_object_attribute.return_value = {
            "result": True,
            "data": [{"bk_property_id": "bk_set_env", "option": [{"id": "test", "name": "Test"}]}],
        }

        response = cc_get_set_env(request, obj_id="set", biz_cc_id=self.biz_cc_id)
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertTrue(content["result"])
        self.assertEqual(content["data"][0]["text"], "Test")


class SelectTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = MagicMock()
        self.user.username = "admin"

    @patch("pipeline_plugins.variables.query.sites.open.select.requests.get")
    def test_variable_select_source_data_proxy_success(self, mock_get):
        request = self.factory.get("/variable_select_source_data_proxy/", {"url": "http://example.com/api"})
        request.user = self.user

        mock_response = MagicMock()
        mock_response.json.return_value = [{"text": "Item 1", "value": "1"}]
        mock_get.return_value = mock_response

        response = variable_select_source_data_proxy(request)
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(content[0]["text"], "Item 1")

    @patch("pipeline_plugins.variables.query.sites.open.select.requests.get")
    def test_variable_select_source_data_proxy_request_fail(self, mock_get):
        request = self.factory.get("/variable_select_source_data_proxy/", {"url": "http://example.com/api"})
        request.user = self.user

        mock_get.side_effect = Exception("Network Error")

        response = variable_select_source_data_proxy(request)
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertIn("请求数据异常", content[0]["text"])

    @patch("pipeline_plugins.variables.query.sites.open.select.requests.get")
    def test_variable_select_source_data_proxy_json_fail(self, mock_get):
        request = self.factory.get("/variable_select_source_data_proxy/", {"url": "http://example.com/api"})
        request.user = self.user

        mock_response = MagicMock()
        mock_response.json.side_effect = Exception("JSON Error")
        mock_response.content = b"Not JSON"
        mock_get.return_value = mock_response

        response = variable_select_source_data_proxy(request)
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(content[0]["text"], "返回数据格式错误，不是合法 JSON 格式")
