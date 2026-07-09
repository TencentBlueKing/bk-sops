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
from rest_framework.exceptions import PermissionDenied

from gcloud.core.apis.drf.viewsets.task_template import TaskTemplatePermission, TaskTemplateViewSet
from gcloud.iam_auth import IAMMeta

TASK_TEMPLATE_FILTER = "gcloud.core.apis.drf.viewsets.task_template.TaskTemplate.objects.filter"
TASK_CONFIG_ENABLE = "gcloud.core.apis.drf.viewsets.task_template.TaskConfig.objects.enable_independent_subprocess"
TEMPLATESCHEME_FILTER = "gcloud.core.apis.drf.viewsets.task_template.TemplateScheme.objects.filter"


def _build_view(action, query_params, kwargs=None):
    view = TaskTemplateViewSet()
    view.action = action
    view.request = SimpleNamespace(query_params=query_params, user=SimpleNamespace(username="tester"))
    view.kwargs = kwargs or {}
    view.format_kwarg = None
    return view


class VerifyWebhookConfigurationPermissionTestCase(TestCase):
    """BAC/SSRF: verify_webhook_configuration 会驱动服务端向外部 URL 发起请求，
    不能仅要求 PROJECT_VIEW(任意项目查看者均可触发出站请求)，应至少要求项目级写意图权限。"""

    def test_verify_webhook_requires_flow_create_not_project_view(self):
        info = TaskTemplatePermission.actions["verify_webhook_configuration"]
        self.assertEqual(info.iam_action, IAMMeta.FLOW_CREATE_ACTION)
        self.assertNotEqual(info.iam_action, IAMMeta.PROJECT_VIEW_ACTION)


class CommonInfoProjectBindingTestCase(TestCase):
    """BAC: common_info 鉴权只校验请求参数 project__id 的 project_view，
    但 get_object 按 pk 取任意模板，必须再校验模板归属，避免跨项目读取流程名称/方案。"""

    def test_common_info__rejects_template_from_other_project(self):
        view = _build_view("common_info", {"project__id": "10"})
        template = SimpleNamespace(project_id=20, name="victim-flow", pipeline_template=SimpleNamespace())
        with patch.object(TaskTemplateViewSet, "get_object", return_value=template):
            with self.assertRaises(PermissionDenied):
                view.common_info(view.request)

    def test_common_info__allows_template_in_authorized_project(self):
        view = _build_view("common_info", {"project__id": "10"})
        template = SimpleNamespace(project_id=10, name="my-flow", pipeline_template=SimpleNamespace())
        scheme_qs = MagicMock()
        scheme_qs.values_list.return_value = [(1, "scheme-1")]
        with patch.object(TaskTemplateViewSet, "get_object", return_value=template):
            with patch(TEMPLATESCHEME_FILTER, MagicMock(return_value=scheme_qs)):
                response = view.common_info(view.request)
        self.assertEqual(response.data["name"], "my-flow")
        self.assertEqual(response.data["schemes"], [{"id": 1, "name": "scheme-1"}])


class EnableIndependentSubprocessProjectBindingTestCase(TestCase):
    """BAC: enable_independent_subprocess 鉴权基于请求参数 project_id，
    必须确认 template 确属该项目，避免借自有项目权限跨项目读取子流程配置。"""

    def test_enable__rejects_template_from_other_project(self):
        view = _build_view("enable_independent_subprocess", {"project_id": "10"}, kwargs={"pk": "55"})
        not_owned_qs = MagicMock()
        not_owned_qs.exists.return_value = False
        with patch(TASK_TEMPLATE_FILTER, MagicMock(return_value=not_owned_qs)):
            with self.assertRaises(PermissionDenied):
                view.enable_independent_subprocess(view.request, pk="55")

    def test_enable__allows_template_in_authorized_project(self):
        view = _build_view("enable_independent_subprocess", {"project_id": "10"}, kwargs={"pk": "55"})
        owned_qs = MagicMock()
        owned_qs.exists.return_value = True
        with patch(TASK_TEMPLATE_FILTER, MagicMock(return_value=owned_qs)):
            with patch(TASK_CONFIG_ENABLE, MagicMock(return_value=True)):
                response = view.enable_independent_subprocess(view.request, pk="55")
        self.assertEqual(response.data, {"enable": True})

    def test_enable__new_template_skips_ownership_check(self):
        """template_id=-1 为新建未保存场景，无归属可校验，应直接放行而不触发归属查询。"""
        view = _build_view("enable_independent_subprocess", {"project_id": "10"}, kwargs={"pk": "-1"})
        filter_mock = MagicMock()
        with patch(TASK_TEMPLATE_FILTER, filter_mock):
            with patch(TASK_CONFIG_ENABLE, MagicMock(return_value=False)):
                response = view.enable_independent_subprocess(view.request, pk="-1")
        filter_mock.assert_not_called()
        self.assertEqual(response.data, {"enable": False})
