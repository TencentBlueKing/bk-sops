# -*- coding: utf-8 -*-
import json
from unittest.mock import MagicMock, patch

from django.test import RequestFactory, TestCase

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


class VariablesQueryTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = MagicMock()
        self.user.username = "admin"
        self.user.tenant_id = "tenant"

    @patch("pipeline_plugins.variables.query.sites.open.query.get_client_by_username")
    @patch("pipeline_plugins.variables.query.sites.open.query.batch_request")
    def test_cc_get_set(self, mock_batch_request, mock_get_client):
        request = self.factory.get("/")
        request.user = self.user

        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        # Mock batch_request return
        mock_batch_request.return_value = [
            {"bk_set_id": 1, "bk_set_name": "set1"},
            {"bk_set_id": 2, "bk_set_name": "set2"},
        ]

        response = cc_get_set(request, "1")

        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertTrue(content["result"])
        self.assertEqual(len(content["data"]), 2)
        self.assertEqual(content["data"][0]["value"], 1)
        self.assertEqual(content["data"][0]["text"], "set1")

    @patch("pipeline_plugins.variables.query.sites.open.query.get_client_by_username")
    @patch("pipeline_plugins.variables.query.sites.open.query.batch_request")
    def test_cc_get_module(self, mock_batch_request, mock_get_client):
        request = self.factory.get("/")
        request.user = self.user

        mock_batch_request.return_value = [{"bk_module_id": 10, "bk_module_name": "mod1"}]

        response = cc_get_module(request, "1", "2")

        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertTrue(content["result"])
        self.assertEqual(len(content["data"]), 1)
        self.assertEqual(content["data"][0]["value"], 10)

    @patch("pipeline_plugins.variables.query.sites.open.query.StaffGroupSet")
    def test_get_staff_groups(self, mock_staff_group_set):
        request = self.factory.get("/")
        request.user = self.user

        mock_qs = MagicMock()
        mock_staff_group_set.objects.filter.return_value = mock_qs
        mock_qs.values.return_value = [{"id": 1, "name": "group1"}]

        response = get_staff_groups(request, "1")

        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertTrue(content["result"])
        self.assertEqual(content["data"][0]["text"], "group1")

    @patch("pipeline_plugins.variables.query.sites.open.query.get_set_list")
    def test_cc_get_set_list(self, mock_get_set_list):
        request = self.factory.get("/")
        request.user = self.user

        mock_get_set_list.return_value = [
            {"bk_set_name": "set1"},
            {"bk_set_name": "set2"},
            {"bk_set_name": "set1"},  # Duplicate
        ]

        response = cc_get_set_list(request, "1")

        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertTrue(content["result"])
        # Should have "all", "set1", "set2" (duplicates removed)
        self.assertEqual(len(content["data"]), 3)
        self.assertEqual(content["data"][0]["value"], "all")

    @patch("pipeline_plugins.variables.query.sites.open.query.get_biz_internal_module")
    @patch("pipeline_plugins.variables.query.sites.open.query.get_service_template_list")
    def test_cc_list_service_template(self, mock_get_svc_tmpl, mock_get_internal):
        request = self.factory.get("/", {"all": "true"})
        request.user = self.user

        mock_get_internal.return_value = {"data": [{"name": "idle"}, {"name": "fault"}]}

        mock_get_svc_tmpl.return_value = [
            {"name": "tmpl1"},
            {"name": "idle"},  # Should be filtered out from template list as it is internal
        ]

        response = cc_list_service_template(request, "1")

        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertTrue(content["result"])
        data = content["data"]
        # Expected: "all", "tmpl1", "idle", "fault"
        self.assertEqual(data[0]["value"], "all")
        self.assertTrue(any(d["value"] == "tmpl1" for d in data))
        self.assertTrue(any(d["value"] == "idle" for d in data))

    @patch("pipeline_plugins.variables.query.sites.open.query.get_client_by_username")
    @patch("pipeline_plugins.variables.query.sites.open.query.batch_request")
    def test_cc_get_set_group(self, mock_batch_request, mock_get_client):
        request = self.factory.get("/")
        request.user = self.user

        mock_batch_request.return_value = [{"id": "g1", "name": "group1"}]

        response = cc_get_set_group(request, "1")

        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertTrue(content["result"])
        self.assertEqual(content["data"][0]["value"], "g1")

    @patch("pipeline_plugins.variables.query.sites.open.query.get_client_by_username")
    def test_cc_get_set_attribute(self, mock_get_client):
        request = self.factory.get("/")
        request.user = self.user

        client = MagicMock()
        mock_get_client.return_value = client

        # Success case
        client.api.search_object_attribute.return_value = {
            "result": True,
            "data": [{"bk_property_id": "p1", "bk_property_name": "prop1"}],
        }

        response = cc_get_set_attribute(request, "1")
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertTrue(content["result"])
        self.assertEqual(content["data"][0]["value"], "p1")

        # Fail case
        client.api.search_object_attribute.return_value = {"result": False, "message": "error"}
        response = cc_get_set_attribute(request, "1")
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertFalse(content["result"])

    @patch("pipeline_plugins.variables.query.sites.open.query.get_client_by_username")
    def test_cc_get_set_env(self, mock_get_client):
        request = self.factory.get("/")
        request.user = self.user

        client = MagicMock()
        mock_get_client.return_value = client

        # Success case
        client.api.search_object_attribute.return_value = {
            "result": True,
            "data": [
                {"bk_property_id": "bk_set_env", "option": [{"id": "1", "name": "env1"}]},
                {"bk_property_id": "other", "option": []},
            ],
        }

        response = cc_get_set_env(request, "obj_id", "1")
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertTrue(content["result"])
        self.assertEqual(content["data"][0]["text"], "env1")

        # Fail case
        client.api.search_object_attribute.return_value = {"result": False, "message": "error", "code": 123}
        response = cc_get_set_env(request, "obj_id", "1")
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertFalse(content["result"])
