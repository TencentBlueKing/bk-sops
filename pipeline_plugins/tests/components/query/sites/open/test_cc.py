# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import json

from django.test import RequestFactory, TestCase
from mock import MagicMock, patch

from gcloud.exceptions import ApiRequestError
from pipeline_plugins.components.query.sites.open.cc import (
    cc_attribute_type_to_table_type,
    cc_find_host_by_topo,
    cc_format_topo_data,
    cc_get_business,
    cc_get_editable_module_attribute,
    cc_get_editable_set_attribute,
    cc_get_service_category_topo,
    cc_input_host_property,
    cc_list_service_category,
    cc_list_service_template,
    cc_search_create_object_attribute,
    cc_search_object_attribute,
    cc_search_object_attribute_all,
    cc_search_status_options,
    cc_search_topo,
    list_business_set,
)


class ComponentsQueryCCTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = MagicMock()
        self.user.username = "admin"
        self.user.tenant_id = "tenant"
        self.request = self.factory.get("/")
        self.request.user = self.user

    @patch("pipeline_plugins.components.query.sites.open.cc.get_client_by_request")
    def test_cc_search_object_attribute(self, mock_get_client):
        client = MagicMock()
        mock_get_client.return_value = client

        # Case 1: Success with include_not_editable=True
        client.api.search_object_attribute.return_value = {
            "result": True,
            "data": [
                {"bk_property_id": "p1", "bk_property_name": "n1", "editable": True},
                {"bk_property_id": "p2", "bk_property_name": "n2", "editable": False},
            ],
        }
        request = self.factory.get("/", {"all": "true"})
        request.user = self.user
        resp = cc_search_object_attribute(request, "obj", 1)
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)["data"]
        self.assertEqual(len(data), 2)

        # Case 2: Error handling
        client.api.search_object_attribute.return_value = {"result": False, "message": "error"}
        resp = cc_search_object_attribute(self.request, "obj", 1)
        self.assertEqual(resp.status_code, 200)
        content = json.loads(resp.content)
        self.assertFalse(content["result"])

    @patch("pipeline_plugins.components.query.sites.open.cc.get_client_by_request")
    def test_cc_search_object_attribute_all(self, mock_get_client):
        client = MagicMock()
        mock_get_client.return_value = client

        # Case 1: Error handling
        client.api.search_object_attribute.return_value = {"result": False, "message": "error"}
        resp = cc_search_object_attribute_all(self.request, "obj", 1)
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(json.loads(resp.content)["result"])

    def test_cc_attribute_type_to_table_type(self):
        # Case 1: int type
        attr = {"bk_property_id": "id", "bk_property_name": "name", "editable": True, "bk_property_type": "int"}
        res = cc_attribute_type_to_table_type(attr)
        self.assertEqual(res["type"], "int")

        # Case 2: enum type with default
        attr = {
            "bk_property_id": "id",
            "bk_property_name": "name",
            "editable": True,
            "bk_property_type": "enum",
            "option": [{"id": "1", "name": "opt1", "is_default": True}],
        }
        res = cc_attribute_type_to_table_type(attr)
        self.assertEqual(res["type"], "select")
        self.assertEqual(res["attrs"]["default"], "1")

    @patch("pipeline_plugins.components.query.sites.open.cc.get_client_by_request")
    def test_cc_search_create_object_attribute(self, mock_get_client):
        client = MagicMock()
        mock_get_client.return_value = client

        # Case 1: Success with validation
        client.api.search_object_attribute.return_value = {
            "result": True,
            "data": [
                {
                    "bk_property_id": "bk_set_name",
                    "bk_property_name": "n1",
                    "editable": True,
                    "bk_property_type": "char",
                },
            ],
        }
        resp = cc_search_create_object_attribute(self.request, "obj", 1)
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)["data"]
        self.assertTrue("validation" in data[0]["attrs"])

        # Case 2: Error handling
        client.api.search_object_attribute.return_value = {"result": False, "message": "error"}
        resp = cc_search_create_object_attribute(self.request, "obj", 1)
        self.assertFalse(json.loads(resp.content)["result"])

    @patch("pipeline_plugins.components.query.sites.open.cc.get_client_by_request")
    def test_cc_list_service_category(self, mock_get_client):
        client = MagicMock()
        mock_get_client.return_value = client

        # Case 1: Error handling
        client.api.list_service_category.return_value = {"result": False, "message": "error"}
        resp = cc_list_service_category(self.request, 1, 0)
        self.assertFalse(json.loads(resp.content)["result"])

        # Case 2: Parent ID filtering
        client.api.list_service_category.return_value = {
            "result": True,
            "data": {"info": [{"id": 1, "name": "c1", "bk_parent_id": 10}, {"id": 2, "name": "c2", "bk_parent_id": 0}]},
        }
        resp = cc_list_service_category(self.request, 1, 0)
        data = json.loads(resp.content)["data"]
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["value"], 2)

    @patch("pipeline_plugins.components.query.sites.open.cc.get_client_by_request")
    def test_cc_get_service_category_topo(self, mock_get_client):
        client = MagicMock()
        mock_get_client.return_value = client

        # Case 1: Error handling
        client.api.list_service_category.return_value = {"result": False, "message": "error"}
        resp = cc_get_service_category_topo(self.request, 1)
        self.assertFalse(json.loads(resp.content)["result"])

        # Case 2: Filtering
        client.api.list_service_category.return_value = {
            "result": True,
            "data": {
                "info": [
                    {"id": 1, "name": "root", "bk_parent_id": 0},
                    {"id": 2, "name": "child", "bk_parent_id": 1},
                    {"id": 3, "name": "orphan", "bk_parent_id": 999},
                ]
            },
        }
        resp = cc_get_service_category_topo(self.request, 1)
        data = json.loads(resp.content)["data"]
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["value"], 1)

    @patch("pipeline_plugins.components.query.sites.open.cc.batch_request")
    @patch("pipeline_plugins.components.query.sites.open.cc.get_client_by_request")
    def test_cc_list_service_template(self, mock_get_client, mock_batch_request):
        client = MagicMock()
        mock_get_client.return_value = client

        # Case 1: ApiRequestError
        mock_batch_request.side_effect = ApiRequestError("error")
        resp = cc_list_service_template(self.request, 1)
        self.assertFalse(json.loads(resp.content)["result"])

    def test_cc_format_topo_data(self):
        # Case 1: prev category
        data = [
            {
                "bk_obj_id": "set",
                "bk_inst_id": 1,
                "bk_inst_name": "set1",
                "child": [{"bk_obj_id": "module", "bk_inst_id": 2, "bk_inst_name": "mod1"}],
            }
        ]
        # category='prev', obj_id='module' -> should show set, and traverse child
        res = cc_format_topo_data(data, "module", "prev")
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]["id"], "set_1")
        # child should be processed
        self.assertTrue("children" in res[0])

    @patch("pipeline_plugins.components.query.sites.open.cc.get_client_by_request")
    def test_cc_search_topo(self, mock_get_client):
        client = MagicMock()
        mock_get_client.return_value = client

        # Case 1: Error handling search_biz_inst_topo
        client.api.search_biz_inst_topo.return_value = {"result": False, "message": "error"}
        resp = cc_search_topo(self.request, "obj", "normal", 1)
        self.assertFalse(json.loads(resp.content)["result"])

        # Case 2: Error handling get_biz_internal_module
        client.api.search_biz_inst_topo.return_value = {"result": True, "data": []}
        client.api.get_biz_internal_module.return_value = {"result": False, "message": "error"}
        request = self.factory.get("/", {"with_internal_module": "true"})
        request.user = self.user
        resp = cc_search_topo(request, "obj", "normal", 1)
        self.assertFalse(json.loads(resp.content)["result"])

        # Case 3: unknown category
        client.api.search_biz_inst_topo.return_value = {"result": True, "data": []}
        resp = cc_search_topo(self.request, "obj", "unknown", 1)
        self.assertEqual(json.loads(resp.content)["data"], [])

    @patch("pipeline_plugins.components.query.sites.open.cc.get_user_business_list")
    def test_cc_get_business(self, mock_get_user_business_list):
        # Case 1: APIError with code != 403
        mock_get_user_business_list.side_effect = ApiRequestError("error")
        # ApiRequestError is subclass of APIError?
        # Let's check imports. gcloud.exceptions.ApiRequestError
        # cc.py catches APIError from gcloud.exceptions
        # Let's check if ApiRequestError inherits APIError.
        # Usually yes.
        # But wait, cc.py catches APIError.
        # Let's try to mock APIError directly if needed, but ApiRequestError should work if it is subclass.
        # If not, I should import APIError.

        # Let's use APIError
        from gcloud.exceptions import APIError

        e = APIError("system", "api", "error")
        e.result = {"code": 0, "permission": {}}
        mock_get_user_business_list.side_effect = e

        resp = cc_get_business(self.request)
        self.assertFalse(json.loads(resp.content)["result"])

        # Case 2: APIError with code == 403 (HTTP_AUTH_FORBIDDEN_CODE)
        from iam.contrib.http import HTTP_AUTH_FORBIDDEN_CODE
        from iam.exceptions import RawAuthFailedException

        e = APIError("system", "api", "error")
        e.result = {"code": HTTP_AUTH_FORBIDDEN_CODE, "permission": {}}
        mock_get_user_business_list.side_effect = e

        with self.assertRaises(RawAuthFailedException):
            cc_get_business(self.request)

    @patch("pipeline_plugins.components.query.sites.open.cc.get_client_by_request")
    def test_cc_get_editable_module_attribute(self, mock_get_client):
        client = MagicMock()
        mock_get_client.return_value = client
        client.api.search_object_attribute.return_value = {"result": False, "message": "error"}
        resp = cc_get_editable_module_attribute(self.request, 1)
        self.assertFalse(json.loads(resp.content)["result"])

    @patch("pipeline_plugins.components.query.sites.open.cc.get_client_by_request")
    def test_cc_input_host_property(self, mock_get_client):
        client = MagicMock()
        mock_get_client.return_value = client
        client.api.search_object_attribute.return_value = {"result": False, "message": "error"}
        resp = cc_input_host_property(self.request, 1)
        self.assertFalse(json.loads(resp.content)["result"])

    @patch("pipeline_plugins.components.query.sites.open.cc.get_client_by_request")
    def test_cc_get_editable_set_attribute(self, mock_get_client):
        client = MagicMock()
        mock_get_client.return_value = client
        client.api.search_object_attribute.return_value = {"result": False, "message": "error"}
        resp = cc_get_editable_set_attribute(self.request, 1)
        self.assertFalse(json.loads(resp.content)["result"])

    @patch("pipeline_plugins.components.query.sites.open.cc.get_client_by_request")
    def test_cc_search_status_options(self, mock_get_client):
        client = MagicMock()
        mock_get_client.return_value = client

        # Case 1: Empty options / Error handling logic
        # If no options found, it logs error and returns result=False
        client.api.search_object_attribute.return_value = {"result": True, "data": []}
        resp = cc_search_status_options(self.request, 1)
        # Wait, if data is empty, options is empty.
        # If options empty, it calls handle_api_error
        self.assertFalse(json.loads(resp.content)["result"])

    @patch("pipeline_plugins.components.query.sites.open.cc.batch_execute_func")
    @patch("pipeline_plugins.components.query.sites.open.cc.get_client_by_request")
    def test_cc_find_host_by_topo(self, mock_get_client, mock_batch_execute):
        client = MagicMock()
        mock_get_client.return_value = client

        # Case 1: Partial failure in batch
        mock_batch_execute.return_value = [
            {"result": {"result": False, "message": "err"}, "params": {"data": {"bk_inst_id": 1}}}
        ]
        resp = cc_find_host_by_topo(self.request, 1)
        self.assertFalse(json.loads(resp.content)["result"])

    @patch("pipeline_plugins.components.query.sites.open.cc.get_client_by_request")
    def test_list_business_set(self, mock_get_client):
        client = MagicMock()
        mock_get_client.return_value = client

        # Case 1: Error handling
        client.api.list_business_set.return_value = {"result": False, "message": ["error"]}
        resp = list_business_set(self.request)
        self.assertFalse(json.loads(resp.content)["result"])
