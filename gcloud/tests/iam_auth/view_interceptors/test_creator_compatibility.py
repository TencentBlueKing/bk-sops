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
from types import SimpleNamespace
from unittest.mock import patch

from django.test import SimpleTestCase

from gcloud.iam_auth.view_interceptors.taskflow import (
    BatchStatusViewInterceptor,
    PreviewTaskTreeInterceptor,
    StatusViewInterceptor,
)
from gcloud.iam_auth.view_interceptors.template import BatchFormInterceptor, TaskTemplateViewInterceptor
from gcloud.tasktmpl3.apis.drf.permissions import (
    BatchTemplateFormWithSchemesPermissions,
    TemplateFormWithSchemesPermissions,
)
from gcloud.template_base.apis.drf.permission import SchemeEditPermission


def _user_request():
    return SimpleNamespace(
        user=SimpleNamespace(username="creator", tenant_id="system"),
        GET={"template_id": "1", "project_id": "10"},
        query_params={"template_id": "1", "project_id": "10"},
        data={},
    )


class CreatorCompatibilityInterceptorTestCase(SimpleTestCase):
    @patch("gcloud.iam_auth.view_interceptors.template.get_iam_client")
    @patch("gcloud.iam_auth.view_interceptors.template.is_flow_creator", return_value=True)
    def test_template_read_skips_remote_iam_for_creator(self, is_creator, get_iam_client):
        TaskTemplateViewInterceptor().process(_user_request())

        is_creator.assert_called_once_with("creator", "system", "1", project_id="10")
        get_iam_client.assert_not_called()

    @patch("gcloud.template_base.apis.drf.permission.get_iam_client")
    @patch("gcloud.template_base.apis.drf.permission.is_flow_creator", return_value=True)
    def test_scheme_read_skips_remote_iam_for_creator(self, is_creator, get_iam_client):
        self.assertTrue(SchemeEditPermission.scheme_allow_or_raise_auth_failed(_user_request(), action="view"))

        is_creator.assert_called_once_with("creator", "system", "1", project_id="10")
        get_iam_client.assert_not_called()

    @patch("gcloud.iam_auth.view_interceptors.taskflow.get_iam_client")
    @patch("gcloud.iam_auth.view_interceptors.taskflow.is_flow_creator", return_value=True)
    def test_task_preview_skips_remote_iam_for_flow_creator(self, is_creator, get_iam_client):
        request = _user_request()
        request.body = json.dumps({"template_id": 1, "template_source": "project"})

        PreviewTaskTreeInterceptor().process(request, project_id=10)

        is_creator.assert_called_once_with("creator", "system", 1, project_id=10)
        get_iam_client.assert_not_called()

    @patch("gcloud.iam_auth.view_interceptors.taskflow.get_iam_client")
    @patch("gcloud.iam_auth.view_interceptors.taskflow.is_task_creator", return_value=True)
    def test_task_runtime_api_skips_remote_iam_for_task_creator(self, is_creator, get_iam_client):
        request = _user_request()
        request.GET = {"instance_id": "20"}

        StatusViewInterceptor().process(request, project_id=10)

        is_creator.assert_called_once_with("creator", "system", "20")
        get_iam_client.assert_not_called()

    @patch("gcloud.tasktmpl3.apis.drf.permissions.IAMMixin.iam_auth_check")
    @patch("gcloud.tasktmpl3.apis.drf.permissions.is_flow_creator", return_value=True)
    def test_form_with_schemes_skips_remote_iam_for_creator(self, is_creator, iam_auth_check):
        request = _user_request()
        request.data = {
            "template_id": "1",
            "template_source": "project",
            "project_id": 10,
        }

        self.assertTrue(TemplateFormWithSchemesPermissions().has_permission(request, None))

        is_creator.assert_called_once_with("creator", "system", "1", project_id=10)
        iam_auth_check.assert_not_called()

    @patch("gcloud.tasktmpl3.apis.drf.permissions.get_iam_client")
    @patch("gcloud.tasktmpl3.apis.drf.permissions.get_flow_creator_ids", return_value={"1", "2"})
    def test_batch_form_with_schemes_skips_remote_iam_for_creators(self, creator_ids, get_iam_client):
        request = _user_request()
        request.data = {"project_id": 10}

        self.assertTrue(
            BatchTemplateFormWithSchemesPermissions().is_allowed_batch_view_flow(request, "project", [1, 2])
        )

        creator_ids.assert_called_once_with("creator", "system", [1, 2], project_id=10)
        get_iam_client.assert_not_called()

    @patch("gcloud.iam_auth.view_interceptors.template.get_iam_client")
    @patch("gcloud.iam_auth.view_interceptors.template.get_flow_creator_ids", return_value={"1", "2"})
    def test_legacy_batch_form_skips_remote_iam_for_creators(self, creator_ids, get_iam_client):
        request = _user_request()
        request.data = {"project_id": 10, "templates": [{"id": 1}, {"id": 2}]}

        BatchFormInterceptor().process(request)

        creator_ids.assert_called_once_with("creator", "system", [1, 2], project_id=10)
        get_iam_client.assert_not_called()

    @patch("gcloud.iam_auth.view_interceptors.taskflow.PermissionService.allowed_resources")
    @patch("gcloud.iam_auth.view_interceptors.taskflow.get_task_creator_ids", return_value={"20"})
    @patch("gcloud.iam_auth.view_interceptors.taskflow.res_factory.resources_list_for_tasks")
    def test_batch_task_status_skips_remote_iam_for_creator(
        self, resources_list_for_tasks, creator_ids, allowed_resources
    ):
        resource = SimpleNamespace(id="20")
        resources_list_for_tasks.return_value = [[resource]]
        request = _user_request()
        request.body = json.dumps({"task_ids": [20]})

        BatchStatusViewInterceptor().process(request)

        creator_ids.assert_called_once_with("creator", "system", [20])
        allowed_resources.assert_not_called()
