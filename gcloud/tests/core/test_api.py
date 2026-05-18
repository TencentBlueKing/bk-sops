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

from django.test import RequestFactory, TestCase
from rest_framework.test import APIRequestFactory

from gcloud.core.api import change_default_project
from gcloud.core.apis.drf.viewsets import CommonProjectViewSet
from gcloud.core.models import Project, ProjectCounter, UserDefaultProject
from gcloud.core.project import get_default_project_for_user


class ChangeDefaultProjectTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.username = "operator"
        self.allowed_project = Project.objects.create(
            name="allowed_project", creator=self.username, bk_biz_id=10001, time_zone="Asia/Shanghai"
        )
        self.denied_project = Project.objects.create(
            name="denied_project", creator="other", bk_biz_id=10002, time_zone="Asia/Shanghai"
        )

    def test_change_default_project_rejects_project_without_view_permission(self):
        request = self.factory.post(f"/core/api/change_default_project/{self.denied_project.id}/")
        request.user = SimpleNamespace(username=self.username)

        with patch(
            "gcloud.core.api.get_user_projects",
            return_value=Project.objects.filter(id=self.allowed_project.id),
        ):
            response = change_default_project(request, self.denied_project.id)

        payload = json.loads(response.content)
        self.assertFalse(payload["result"])
        self.assertFalse(UserDefaultProject.objects.filter(username=self.username).exists())
        self.assertFalse(ProjectCounter.objects.filter(username=self.username, project=self.denied_project).exists())

    def test_change_default_project_records_project_with_view_permission(self):
        request = self.factory.post(f"/core/api/change_default_project/{self.allowed_project.id}/")
        request.user = SimpleNamespace(username=self.username)

        with patch(
            "gcloud.core.api.get_user_projects",
            return_value=Project.objects.filter(id=self.allowed_project.id),
        ):
            response = change_default_project(request, self.allowed_project.id)

        payload = json.loads(response.content)
        self.assertTrue(payload["result"])
        self.assertEqual(
            UserDefaultProject.objects.get(username=self.username).default_project_id,
            self.allowed_project.id,
        )
        self.assertTrue(ProjectCounter.objects.filter(username=self.username, project=self.allowed_project).exists())


class CommonProjectViewSetTestCase(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.username = "operator"
        self.allowed_project = Project.objects.create(
            name="allowed_project", creator=self.username, bk_biz_id=10001, time_zone="Asia/Shanghai"
        )
        self.denied_project = Project.objects.create(
            name="denied_project", creator="other", bk_biz_id=10002, time_zone="Asia/Shanghai"
        )
        ProjectCounter.objects.create(username=self.username, project=self.allowed_project)
        ProjectCounter.objects.create(username=self.username, project=self.denied_project)

    def test_list_filters_out_project_without_view_permission(self):
        request = self.factory.get("/api/v3/common_project/")
        request.user = SimpleNamespace(username=self.username, is_authenticated=True, is_active=True)
        view = CommonProjectViewSet.as_view({"get": "list"})

        with patch(
            "gcloud.core.apis.drf.viewsets.common_project.get_user_projects",
            return_value=Project.objects.filter(id=self.allowed_project.id),
        ):
            response = view(request)

        project_ids = {item["project"]["id"] for item in response.data["data"]["results"]}
        self.assertEqual(project_ids, {self.allowed_project.id})

    def test_list_initializes_common_projects_with_single_user_project_lookup(self):
        ProjectCounter.objects.all().delete()
        request = self.factory.get("/api/v3/common_project/")
        request.user = SimpleNamespace(username=self.username, is_authenticated=True, is_active=True)
        view = CommonProjectViewSet.as_view({"get": "list"})

        with patch(
            "gcloud.core.apis.drf.viewsets.common_project.get_user_projects",
            return_value=Project.objects.filter(id=self.allowed_project.id),
        ) as mock_get_user_projects:
            response = view(request)

        project_ids = {item["project"]["id"] for item in response.data["data"]["results"]}
        self.assertEqual(project_ids, {self.allowed_project.id})
        self.assertEqual(mock_get_user_projects.call_count, 1)


class GetDefaultProjectForUserTestCase(TestCase):
    def setUp(self):
        self.username = "operator"
        self.allowed_project = Project.objects.create(
            name="allowed_project", creator=self.username, bk_biz_id=10001, time_zone="Asia/Shanghai"
        )
        self.denied_project = Project.objects.create(
            name="denied_project", creator="other", bk_biz_id=10002, time_zone="Asia/Shanghai"
        )
        UserDefaultProject.objects.create(username=self.username, default_project=self.denied_project)

    def test_get_default_project_falls_back_when_saved_project_has_no_view_permission(self):
        with patch(
            "gcloud.core.project.get_user_projects",
            return_value=Project.objects.filter(id=self.allowed_project.id),
        ):
            project = get_default_project_for_user(self.username)

        self.assertEqual(project.id, self.allowed_project.id)
