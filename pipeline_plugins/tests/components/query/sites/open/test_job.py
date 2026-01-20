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

from pipeline_plugins.components.query.sites.open.job import (
    job_get_instance_detail,
    job_get_job_task_detail,
    job_get_script_list,
    jobv3_get_instance_list,
    jobv3_get_job_plan_detail,
)


class ComponentsQueryJobTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = MagicMock()
        self.user.username = "admin"
        self.user.tenant_id = "tenant"
        self.request = self.factory.get("/")
        self.request.user = self.user

    @patch("pipeline_plugins.components.query.sites.open.job.get_client_by_username")
    def test_job_get_job_task_detail(self, mock_get_client):
        client = MagicMock()
        mock_get_client.return_value = client

        # Case 1: Error handling
        client.api.get_job_plan_detail.return_value = {"result": False, "message": "error"}
        resp = job_get_job_task_detail(self.request, 1, 1)
        self.assertFalse(json.loads(resp.content)["result"])

        # Case 2: Empty task detail
        client.api.get_job_plan_detail.return_value = {"result": True, "data": None}
        resp = job_get_job_task_detail(self.request, 1, 1)
        self.assertFalse(json.loads(resp.content)["result"])

        # Case 3: Unknown var type
        client.api.get_job_plan_detail.return_value = {
            "result": True,
            "data": {"global_var_list": [{"type": 999, "used": True, "name": "unknown"}], "step_list": []},
        }
        resp = job_get_job_task_detail(self.request, 1, 1)
        data = json.loads(resp.content)["data"]
        self.assertEqual(len(data["global_var"]), 0)

    @patch("pipeline_plugins.components.query.sites.open.job.get_client_by_username")
    def test_jobv3_get_job_plan_detail(self, mock_get_client):
        client = MagicMock()
        mock_get_client.return_value = client

        # Case 1: Error handling
        client.api.get_job_plan_detail.return_value = {"result": False, "message": "error"}
        resp = jobv3_get_job_plan_detail(self.request, 1, 1)
        self.assertFalse(json.loads(resp.content)["result"])

        # Case 2: Empty plan detail
        client.api.get_job_plan_detail.return_value = {"result": True, "data": None}
        resp = jobv3_get_job_plan_detail(self.request, 1, 1)
        self.assertFalse(json.loads(resp.content)["result"])

        # Case 3: Unknown var type
        client.api.get_job_plan_detail.return_value = {
            "result": True,
            "data": {"global_var_list": [{"type": 999, "name": "unknown"}]},
        }
        resp = jobv3_get_job_plan_detail(self.request, 1, 1)
        self.assertFalse(json.loads(resp.content)["result"])

    @patch("pipeline_plugins.components.query.sites.open.job.get_client_by_username")
    def test_jobv3_get_instance_list(self, mock_get_client):
        client = MagicMock()
        mock_get_client.return_value = client

        # Case 1: Error handling
        client.api.get_job_instance_list.return_value = {"result": False, "message": "error"}
        resp = jobv3_get_instance_list(self.request, 1, 1, 1)
        self.assertFalse(json.loads(resp.content)["result"])

        # Case 2: Empty result
        client.api.get_job_instance_list.return_value = {"result": True, "data": {"data": []}}
        resp = jobv3_get_instance_list(self.request, 1, 1, 1)
        self.assertTrue(json.loads(resp.content)["result"])
        self.assertEqual(json.loads(resp.content)["data"], [])

    @patch("pipeline_plugins.components.query.sites.open.job.get_client_by_username")
    def test_job_get_instance_detail(self, mock_get_client):
        client = MagicMock()
        mock_get_client.return_value = client

        # Case 1: Error handling
        client.api.get_job_instance_ip_log.return_value = {"result": False, "message": "error"}
        resp = job_get_instance_detail(self.request, 1, 1)
        self.assertFalse(json.loads(resp.content)["result"])

    @patch("pipeline_plugins.components.query.sites.open.job.batch_request")
    @patch("pipeline_plugins.components.query.sites.open.job.get_client_by_username")
    def test_job_get_script_list(self, mock_get_client, mock_batch_request):
        # Case 1: public script
        request = self.factory.get("/", {"type": "public"})
        request.user = self.user
        mock_batch_request.return_value = []
        resp = job_get_script_list(request, 1)
        self.assertEqual(resp.status_code, 200)

        # Case 2: value field parsing
        mock_batch_request.return_value = [{"name": "s1", "id": 10}, {"name": "s1", "id": 5}]
        request = self.factory.get("/")
        request.user = self.user
        resp = job_get_script_list(request, 1)
        data = json.loads(resp.content)["data"]
        # Should take max version
        self.assertEqual(data[0]["value"], 10)
