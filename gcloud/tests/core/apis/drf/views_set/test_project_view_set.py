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

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.test import TestCase

from gcloud.core.apis.drf.viewsets.project import ProjectSetViewSet
from gcloud.core.models import Project

GET_USER_PROJECTS = "gcloud.core.apis.drf.viewsets.project.get_user_projects"


class ProjectSetListScopeTestCase(TestCase):
    """BAC: ProjectSetViewSet.list 原先 pass_all，会向任意登录用户暴露全平台项目清单。
    修复后 list 必须收敛到当前用户有查看权限的项目，非 list 行为不受影响。"""

    def setUp(self):
        Project.objects.all().delete()
        self.p1 = Project.objects.create(name="bac-p1", creator="tester", bk_biz_id=9001)
        self.p2 = Project.objects.create(name="bac-p2", creator="tester", bk_biz_id=9002)
        self.p3 = Project.objects.create(name="bac-p3", creator="tester", bk_biz_id=9003)

    def tearDown(self):
        Project.objects.all().delete()

    def _build_view(self, action):
        view = ProjectSetViewSet()
        view.action = action
        view.request = SimpleNamespace(user=SimpleNamespace(username="tester"))
        view.kwargs = {}
        view.format_kwarg = None
        return view

    def test_list_scopes_to_user_authorized_projects(self):
        view = self._build_view("list")
        authorized = MagicMock()
        authorized.values_list.return_value = [self.p1.id, self.p3.id]
        with patch(GET_USER_PROJECTS, MagicMock(return_value=authorized)):
            queryset = view.get_queryset()
        self.assertEqual(set(queryset.values_list("id", flat=True)), {self.p1.id, self.p3.id})

    def test_non_list_action_returns_full_queryset(self):
        view = self._build_view("retrieve")
        with patch(GET_USER_PROJECTS) as get_user_projects:
            queryset = view.get_queryset()
        get_user_projects.assert_not_called()
        self.assertEqual(
            set(queryset.values_list("id", flat=True)),
            {self.p1.id, self.p2.id, self.p3.id},
        )
