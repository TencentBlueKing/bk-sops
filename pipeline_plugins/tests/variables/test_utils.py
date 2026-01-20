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

from django.test import TestCase
from mock import MagicMock, patch

from gcloud.exceptions import ApiRequestError
from pipeline_plugins.variables.utils import (
    filter_ip,
    find_module_with_relation,
    get_biz_internal_module,
    get_list_by_selected_names,
    get_module_list,
    get_service_template_list,
    get_service_template_list_by_names,
    get_set_list,
    list_biz_hosts,
)

LIST_BIZ_HOSTS_SUCCESS_RETURN = [{"bk_host_innerip": "192.168.15.18"}, {"bk_host_innerip": "192.168.15.4"}]
PROC_STATUS_ERROR_RETURN = []

MULTIPLE_SUCCESS_KWARGS = {"bk_module_ids": [i for i in range(1000)], "fields": ["bk_host_innerip"]}

SUCCESS_RESULT = [
    {"bk_host_innerip": "192.168.15.18"},
    {"bk_host_innerip": "192.168.15.4"},
    {"bk_host_innerip": "192.168.15.18"},
    {"bk_host_innerip": "192.168.15.4"},
]
ERROR_RESULT = ""
LIST_BIZ_HOSTS_CLIENT = "pipeline_plugins.variables.utils.batch_request"


class UtilsTestCase(TestCase):
    @patch(LIST_BIZ_HOSTS_CLIENT)
    def test_list_biz_hosts(self, batch_request_patch):
        batch_request_patch.return_value = LIST_BIZ_HOSTS_SUCCESS_RETURN
        result = list_biz_hosts(
            tenant_id="test",
            username="admin",
            bk_biz_id="123",
            kwargs=MULTIPLE_SUCCESS_KWARGS,
        )
        self.assertEqual(SUCCESS_RESULT, result)
        self.assertEqual(batch_request_patch.call_count, 2)

    def test_filter_ip(self):
        origin = "1.1.1.1,2.2.2.2,3.3.3.3"
        filter_str = "1.1.1.1,3.3.3.3"
        result = filter_ip(origin, filter_str)
        self.assertTrue("1.1.1.1" in result)
        self.assertTrue("3.3.3.3" in result)
        self.assertTrue("2.2.2.2" not in result)

    def test_get_list_by_selected_names(self):
        set_list = [{"bk_set_id": 1, "bk_set_name": "a"}, {"bk_set_id": 2, "bk_set_name": "b"}]
        # List input
        res = get_list_by_selected_names(["a"], set_list)
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]["bk_set_name"], "a")
        # String input
        res = get_list_by_selected_names("b", set_list)
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]["bk_set_name"], "b")

    def test_get_service_template_list_by_names(self):
        tmpl_list = [{"id": 1, "name": "a"}, {"id": 2, "name": "b"}]
        # List input
        res = get_service_template_list_by_names(["a"], tmpl_list)
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]["name"], "a")
        # String input
        res = get_service_template_list_by_names("b", tmpl_list)
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]["name"], "b")

    @patch("pipeline_plugins.variables.utils.get_client_by_username")
    def test_get_module_list(self, mock_get_client):
        client = MagicMock()
        mock_get_client.return_value = client
        client.api.find_module_batch.return_value = {"result": True, "data": [{"bk_module_id": 1}]}

        res = get_module_list("tenant", "user", 1)
        self.assertEqual(len(res), 1)

        # Test error
        client.api.find_module_batch.return_value = {"result": False, "message": "err", "code": 1}
        with self.assertRaises(ApiRequestError):
            get_module_list("tenant", "user", 1)

    @patch("pipeline_plugins.variables.utils.get_client_by_username")
    @patch("pipeline_plugins.variables.utils.batch_request")
    def test_get_set_list(self, mock_batch_req, mock_get_client):
        mock_batch_req.return_value = [{"bk_set_id": 1}]
        res = get_set_list("tenant", "user", 1)
        self.assertEqual(len(res), 1)

    @patch("pipeline_plugins.variables.utils.get_client_by_username")
    @patch("pipeline_plugins.variables.utils.batch_request")
    def test_get_service_template_list(self, mock_batch_req, mock_get_client):
        mock_batch_req.return_value = [{"id": 1}]
        res = get_service_template_list("tenant", "user", 1)
        self.assertEqual(len(res), 1)

    @patch("pipeline_plugins.variables.utils.get_client_by_username")
    @patch("pipeline_plugins.variables.utils.batch_request")
    def test_find_module_with_relation(self, mock_batch_req, mock_get_client):
        mock_batch_req.return_value = [{"bk_module_id": 1}]
        # Need enough set_ids to trigger loop if step is small, but step is 200.
        res = find_module_with_relation("tenant", 1, "user", [1, 2], [3], [])
        # We pass 2 set_ids, step is 200, so loop runs once.
        # batch_request returns [{"bk_module_id": 1}]
        self.assertEqual(len(res), 1)

    @patch("pipeline_plugins.variables.utils.get_client_by_username")
    def test_get_biz_internal_module(self, mock_get_client):
        client = MagicMock()
        mock_get_client.return_value = client
        client.api.get_biz_internal_module.return_value = {
            "result": True,
            "data": {"module": [{"bk_module_id": 1, "bk_module_name": "idle"}]},
        }
        res = get_biz_internal_module("tenant", "user", 1)
        self.assertTrue(res["result"])
        self.assertEqual(res["data"][0]["id"], 1)

        # Test error
        client.api.get_biz_internal_module.return_value = {"result": False, "message": "err", "code": 1}
        with self.assertRaises(ApiRequestError):
            get_biz_internal_module("tenant", "user", 1)
