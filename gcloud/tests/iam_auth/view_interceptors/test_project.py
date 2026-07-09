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
from unittest import TestCase, mock

from iam.exceptions import AuthFailedException

from gcloud.core.models import Project
from gcloud.iam_auth import IAMMeta
from gcloud.iam_auth.view_interceptors.project import ProjectFlowCreateInterceptor, ProjectViewInterceptor

ALLOW_OR_RAISE_PATH = "gcloud.iam_auth.view_interceptors.project.allow_or_raise_auth_failed"
RESOURCES_FOR_PROJECT_PATH = "gcloud.iam_auth.view_interceptors.project.res_factory.resources_for_project"


class ProjectInterceptorTestCase(TestCase):
    def setUp(self):
        self.request = SimpleNamespace(user=SimpleNamespace(username="tester"), GET={}, POST={})

    @mock.patch(RESOURCES_FOR_PROJECT_PATH, return_value=["project-resource"])
    @mock.patch(ALLOW_OR_RAISE_PATH)
    def test_project_view__uses_kwargs_project_id_and_project_view_action(
        self, mocked_allow_or_raise, mocked_resources_for_project
    ):
        ProjectViewInterceptor().process(self.request, project_id=42)

        mocked_resources_for_project.assert_called_once_with(42)
        mocked_allow_or_raise.assert_called_once()
        kwargs = mocked_allow_or_raise.call_args[1]
        self.assertEqual(kwargs["system"], IAMMeta.SYSTEM_ID)
        self.assertEqual(kwargs["subject"].type, "user")
        self.assertEqual(kwargs["subject"].id, "tester")
        self.assertEqual(kwargs["action"].id, IAMMeta.PROJECT_VIEW_ACTION)
        self.assertEqual(kwargs["resources"], ["project-resource"])
        self.assertTrue(kwargs.get("cache"))

    @mock.patch(RESOURCES_FOR_PROJECT_PATH, return_value=["project-resource"])
    @mock.patch(ALLOW_OR_RAISE_PATH)
    def test_project_flow_create__uses_flow_create_action(self, mocked_allow_or_raise, mocked_resources_for_project):
        ProjectFlowCreateInterceptor().process(self.request, project_id=7)

        mocked_resources_for_project.assert_called_once_with(7)
        mocked_allow_or_raise.assert_called_once()
        kwargs = mocked_allow_or_raise.call_args[1]
        self.assertEqual(kwargs["action"].id, IAMMeta.FLOW_CREATE_ACTION)

    @mock.patch(RESOURCES_FOR_PROJECT_PATH, return_value=[])
    @mock.patch(ALLOW_OR_RAISE_PATH)
    def test_project_view__fallback_to_query_params_when_kwargs_missing(
        self, mocked_allow_or_raise, mocked_resources_for_project
    ):
        request = SimpleNamespace(
            user=SimpleNamespace(username="tester"),
            GET={"project_id": "9"},
            POST={},
        )

        ProjectViewInterceptor().process(request)

        mocked_resources_for_project.assert_called_once_with("9")
        mocked_allow_or_raise.assert_called_once()

    @mock.patch(RESOURCES_FOR_PROJECT_PATH, return_value=[])
    @mock.patch(ALLOW_OR_RAISE_PATH)
    def test_project_view__fallback_to_post_body_when_query_missing(
        self, mocked_allow_or_raise, mocked_resources_for_project
    ):
        request = SimpleNamespace(
            user=SimpleNamespace(username="tester"),
            GET={},
            POST={"project_id": "11"},
        )

        ProjectViewInterceptor().process(request)

        mocked_resources_for_project.assert_called_once_with("11")
        mocked_allow_or_raise.assert_called_once()

    @mock.patch(RESOURCES_FOR_PROJECT_PATH, return_value=[])
    @mock.patch(ALLOW_OR_RAISE_PATH)
    def test_project_view__kwargs_project_id_takes_precedence(
        self, mocked_allow_or_raise, mocked_resources_for_project
    ):
        """URL 路径中的 project_id 必须优先于请求体/查询串里的 project_id，
        防御攻击者用 query/body 中伪造的项目 ID 通过鉴权后访问 URL 真实 project_id 的数据。"""
        request = SimpleNamespace(
            user=SimpleNamespace(username="tester"),
            GET={"project_id": "999"},
            POST={"project_id": "888"},
        )

        ProjectViewInterceptor().process(request, project_id=1)

        mocked_resources_for_project.assert_called_once_with(1)

    @mock.patch(RESOURCES_FOR_PROJECT_PATH, return_value=["project-resource"])
    @mock.patch(ALLOW_OR_RAISE_PATH)
    def test_project_view__missing_project_id_raises_auth_failed_not_500(
        self, mocked_allow_or_raise, mocked_resources_for_project
    ):
        """kwargs/GET/POST 均无 project_id 时，应直接按鉴权失败处理，
        不能进入 resources_for_project(None) 触发 Project.DoesNotExist 造成 500。"""
        with self.assertRaises(AuthFailedException):
            ProjectViewInterceptor().process(self.request)

        mocked_resources_for_project.assert_not_called()
        mocked_allow_or_raise.assert_not_called()

    @mock.patch(RESOURCES_FOR_PROJECT_PATH, side_effect=Project.DoesNotExist)
    @mock.patch(ALLOW_OR_RAISE_PATH)
    def test_project_view__nonexistent_project_raises_auth_failed_not_500(
        self, mocked_allow_or_raise, mocked_resources_for_project
    ):
        """指向不存在项目的 project_id 应按鉴权失败(403)处理，而非把 DoesNotExist 暴露为 500。"""
        with self.assertRaises(AuthFailedException):
            ProjectViewInterceptor().process(self.request, project_id=999999)

        mocked_resources_for_project.assert_called_once_with(999999)
        mocked_allow_or_raise.assert_not_called()
