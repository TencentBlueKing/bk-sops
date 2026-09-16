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

from gcloud.core.apis.drf.permission import IamPermission
from gcloud.core.apis.drf.viewsets.base import GcloudCommonMixin
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


class TaskTemplateCreatorPermissionTestCase(TestCase):
    def test_creator_object_permission_does_not_depend_on_remote_grant(self):
        request = SimpleNamespace(user=SimpleNamespace(username="creator"))
        template = SimpleNamespace(pipeline_template=SimpleNamespace(creator="creator"))

        with patch.object(IamPermission, "has_object_permission") as parent_check:
            self.assertTrue(TaskTemplatePermission().has_object_permission(request, SimpleNamespace(), template))
        parent_check.assert_not_called()

    def test_non_creator_object_permission_uses_iam(self):
        request = SimpleNamespace(user=SimpleNamespace(username="other"))
        template = SimpleNamespace(pipeline_template=SimpleNamespace(creator="creator"))

        with patch.object(IamPermission, "has_object_permission", return_value=False) as parent_check:
            self.assertFalse(TaskTemplatePermission().has_object_permission(request, SimpleNamespace(), template))
        parent_check.assert_called_once()

    def test_creator_gets_all_flow_actions_in_list_response(self):
        request = SimpleNamespace(user=SimpleNamespace(username="creator", tenant_id="system"))
        template = SimpleNamespace(id=1, pipeline_template=SimpleNamespace(creator="creator"))
        data = [{"id": 1, "auth_actions": []}]
        actions = [IAMMeta.FLOW_VIEW_ACTION, IAMMeta.FLOW_CREATE_PERIODIC_TASK_ACTION]

        with patch.object(GcloudCommonMixin, "injection_auth_actions", return_value=data):
            with patch.object(
                TaskTemplateViewSet, "iam_resource_helper", return_value=SimpleNamespace(actions=actions)
            ):
                result = TaskTemplateViewSet().injection_auth_actions(request, data, [template])

        self.assertEqual(result[0]["auth_actions"], actions)


class TaskTemplateWebhookUpdateTestCase(TestCase):
    @patch("gcloud.core.apis.drf.viewsets.task_template.bk_audit_add_event")
    @patch("gcloud.core.apis.drf.viewsets.task_template.operate_record_signal.send")
    @patch("gcloud.core.apis.drf.viewsets.task_template.post_template_save_commit.send")
    @patch("gcloud.core.apis.drf.viewsets.task_template.clear_scope_webhooks")
    @patch("gcloud.core.apis.drf.viewsets.task_template.manager.update_pipeline")
    @patch("gcloud.core.apis.drf.viewsets.task_template.CreateTaskTemplateSerializer")
    def test_disable_webhook_clears_config_when_saving_template(
        self,
        serializer_cls,
        update_pipeline,
        clear_scope_webhooks,
        post_template_save,
        operate_record,
        audit_event,
    ):
        template = SimpleNamespace(
            id=5,
            project_id=42,
            project=SimpleNamespace(id=42),
            pipeline_template=SimpleNamespace(),
            is_deleted=False,
        )
        serializer = MagicMock()
        serializer.validated_data = {
            "name": "flow",
            "pipeline_tree": "{}",
            "description": "",
            "webhook_configs": {},
            "enable_webhook": False,
            "template_labels": [],
        }
        serializer.instance = template
        serializer.data = {"id": 5}
        serializer_cls.return_value = serializer
        update_pipeline.return_value = {"result": True}
        clear_scope_webhooks.return_value = {"result": True}
        request = SimpleNamespace(data={}, user=SimpleNamespace(username="tester"))
        view = TaskTemplateViewSet()

        with patch.object(view, "get_object", return_value=template), patch.object(
            view, "perform_update"
        ), patch.object(view, "_sync_template_lables"), patch.object(
            view, "injection_auth_actions", return_value={"id": 5}
        ):
            response = view.update(request, partial=True)

        self.assertEqual(response.data, {"id": 5})
        clear_scope_webhooks.assert_called_once_with(["5"])
        post_template_save.assert_called_once()
        operate_record.assert_called_once()
        audit_event.assert_called_once()


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
