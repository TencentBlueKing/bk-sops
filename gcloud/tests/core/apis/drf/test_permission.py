# -*- coding: utf-8 -*-
from copy import copy
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase

from gcloud.core.apis.drf.viewsets.appmaker import AppmakerListViewSet, AppmakerPermission
from gcloud.core.apis.drf.viewsets.base import GcloudReadOnlyViewSet
from gcloud.core.apis.drf.viewsets.common_template import CommonTemplateViewSet
from gcloud.core.apis.drf.viewsets.project import ProjectPermission
from gcloud.iam_auth import IAMMeta, res_factory
from gcloud.iam_auth.exceptions import IAMPermissionDenied
from gcloud.iam_auth.models import Action
from gcloud.iam_auth.types import AuthorizedScope
from gcloud.iam_auth.utils import get_common_flow_allowed_actions_for_user_and_project


class IamPermissionTestCase(SimpleTestCase):
    def test_object_resource_factory_receives_request_tenant_id(self):
        resource_func = MagicMock(return_value=["resource"])
        permission = ProjectPermission()
        permission.actions = dict(permission.actions)
        permission.actions["partial_update"] = copy(permission.actions["partial_update"])
        permission.actions["partial_update"].resource_func = resource_func
        permission.iam_auth_check = MagicMock()
        request = SimpleNamespace(
            user=SimpleNamespace(tenant_id="tenant-a"),
            query_params={},
            data={},
        )
        view = SimpleNamespace(action="partial_update")
        obj = SimpleNamespace(id=1, name="project-a")

        self.assertTrue(permission.has_object_permission(request, view, obj))
        resource_func.assert_called_once_with(obj, "tenant-a")
        permission.iam_auth_check.assert_called_once_with(
            request,
            action=permission.actions["partial_update"].iam_action,
            resources=["resource"],
        )

    @patch("gcloud.core.apis.drf.viewsets.project.PermissionService")
    def test_project_detail_allows_project_common_create_task_permission(self, permission_service):
        permission_service.return_value.allowed_actions.return_value = {
            IAMMeta.PROJECT_VIEW_ACTION: False,
            IAMMeta.PROJECT_COMMON_CREATE_TASK_ACTION: True,
        }
        request = SimpleNamespace(
            user=SimpleNamespace(username="alice", tenant_id="tenant-a"),
            query_params={},
            data={},
        )
        project = SimpleNamespace(id=1, name="project-a")

        self.assertTrue(ProjectPermission().has_object_permission(request, SimpleNamespace(action="retrieve"), project))
        permission_service.return_value.allowed_actions.assert_called_once()

    @patch("gcloud.core.apis.drf.viewsets.project.PermissionService")
    def test_project_detail_denial_still_requests_project_view(self, permission_service):
        permission_service.return_value.allowed_actions.return_value = {
            IAMMeta.PROJECT_VIEW_ACTION: False,
            IAMMeta.PROJECT_COMMON_CREATE_TASK_ACTION: False,
        }
        request = SimpleNamespace(
            user=SimpleNamespace(username="alice", tenant_id="tenant-a"),
            query_params={},
            data={},
        )
        project = SimpleNamespace(id=1, name="project-a")

        with self.assertRaises(IAMPermissionDenied) as context:
            ProjectPermission().has_object_permission(request, SimpleNamespace(action="retrieve"), project)

        self.assertEqual(context.exception.missing_permissions[0].action_id, IAMMeta.PROJECT_VIEW_ACTION)

    @patch("gcloud.taskflow3.models.TaskFlowInstance.objects.filter")
    @patch("gcloud.core.apis.drf.viewsets.project.PermissionService")
    def test_project_detail_allows_reexecute_task_view_permission(self, permission_service, task_filter):
        permission_service.return_value.allowed_actions.return_value = {
            IAMMeta.PROJECT_VIEW_ACTION: False,
            IAMMeta.PROJECT_COMMON_CREATE_TASK_ACTION: False,
        }
        permission_service.return_value.is_allowed.return_value = True
        task_filter.return_value.exists.return_value = True
        request = SimpleNamespace(
            user=SimpleNamespace(username="alice", tenant_id="tenant-a"),
            query_params={"reexecute_task_id": "99"},
            data={},
        )
        project = SimpleNamespace(id=1, name="project-a")

        with patch("gcloud.core.apis.drf.viewsets.project.res_factory.resources_for_task") as task_resources:
            task_resource = SimpleNamespace(type=IAMMeta.TASK_RESOURCE, id="99", attribute={})
            task_resources.return_value = [task_resource]
            allowed = ProjectPermission().has_object_permission(request, SimpleNamespace(action="retrieve"), project)

        self.assertTrue(allowed)
        task_filter.assert_called_once_with(id="99", project_id=1, project__tenant_id="tenant-a", is_deleted=False)
        permission_service.return_value.is_allowed.assert_called_once()

    def test_project_object_factory_supports_permission_and_legacy_call_signatures(self):
        project = SimpleNamespace(id=1, name="project-a")

        legacy_resources = res_factory.resources_for_project_obj(project)
        tenant_resources = res_factory.resources_for_project_obj(project, "tenant-a")

        self.assertEqual(tenant_resources, legacy_resources)
        self.assertEqual(tenant_resources[0].id, "1")
        self.assertEqual(tenant_resources[0].attribute, {"name": "project-a"})


class CommonTemplatePermissionInjectionTestCase(SimpleTestCase):
    @patch("gcloud.iam_auth.utils.PermissionService")
    @patch("gcloud.iam_auth.utils.get_resources_allowed_actions_for_user")
    @patch("gcloud.iam_auth.utils.res_factory.resources_for_project")
    @patch("gcloud.iam_auth.utils.res_factory.resources_list_for_common_flows")
    def test_dual_permission_result_includes_project_view(
        self, common_resources, project_resources, get_common_actions, permission_service
    ):
        common_resources.return_value = [[SimpleNamespace(id="7")]]
        project_resource = SimpleNamespace(id="42")
        project_resources.return_value = [project_resource]
        get_common_actions.return_value = {"7": {IAMMeta.COMMON_FLOW_CREATE_TASK_ACTION: True}}
        permission_service.return_value.allowed_actions.return_value = {
            IAMMeta.PROJECT_COMMON_CREATE_TASK_ACTION: True,
            IAMMeta.PROJECT_VIEW_ACTION: True,
        }

        result = get_common_flow_allowed_actions_for_user_and_project(
            "alice",
            [IAMMeta.COMMON_FLOW_CREATE_TASK_ACTION],
            [7],
            "42",
            "tenant-a",
        )

        self.assertTrue(result["7"][IAMMeta.COMMON_FLOW_CREATE_TASK_ACTION])
        self.assertTrue(result["7"][IAMMeta.PROJECT_COMMON_CREATE_TASK_ACTION])
        self.assertTrue(result["7"][IAMMeta.PROJECT_VIEW_ACTION])
        permission_service.return_value.allowed_actions.assert_called_once_with(
            "alice",
            "tenant-a",
            [IAMMeta.PROJECT_COMMON_CREATE_TASK_ACTION, IAMMeta.PROJECT_VIEW_ACTION],
            project_resource,
        )

    @patch("gcloud.core.apis.drf.viewsets.common_template." "get_common_flow_allowed_actions_for_user_and_project")
    def test_create_task_action_requires_common_flow_and_project_permissions(self, get_allowed_actions):
        get_allowed_actions.return_value = {
            "1": {IAMMeta.COMMON_FLOW_CREATE_TASK_ACTION: True},
            "2": {IAMMeta.COMMON_FLOW_CREATE_TASK_ACTION: False},
        }
        request = SimpleNamespace(
            user=SimpleNamespace(username="alice", tenant_id="tenant-a"),
            query_params={"project_id": "10"},
        )

        allowed_ids = CommonTemplateViewSet._inject_project_based_task_create_action(
            request,
            [1, 2],
            Action(IAMMeta.COMMON_FLOW_CREATE_TASK_ACTION),
        )

        self.assertEqual(allowed_ids, [1])
        get_allowed_actions.assert_called_once_with(
            "alice",
            [IAMMeta.COMMON_FLOW_CREATE_TASK_ACTION],
            [1, 2],
            "10",
            "tenant-a",
        )


class AppmakerPermissionTestCase(SimpleTestCase):
    def test_capabilities_requires_project_view_permission(self):
        permission_info = AppmakerPermission.actions["capabilities"]

        self.assertEqual(permission_info.iam_action, IAMMeta.PROJECT_VIEW_ACTION)
        self.assertEqual(permission_info.id_field, "project__id")

    @patch("gcloud.core.apis.drf.viewsets.appmaker.ScopeResolver")
    @patch.object(GcloudReadOnlyViewSet, "get_queryset")
    def test_list_queryset_is_limited_to_authorized_mini_apps(self, get_queryset, scope_resolver):
        queryset = get_queryset.return_value
        scope_resolver.return_value.authorized_scope.return_value = AuthorizedScope(
            {IAMMeta.MINI_APP_RESOURCE: {"1", "2"}}
        )
        view = AppmakerListViewSet()
        view.action = "list"
        view.request = SimpleNamespace(user=SimpleNamespace(username="alice", tenant_id="tenant-a"))

        result = view.get_queryset()

        self.assertEqual(result, queryset.filter.return_value)
        queryset.filter.assert_called_once_with(id__in={"1", "2"})
        scope_resolver.return_value.authorized_scope.assert_called_once_with(
            "alice", "tenant-a", IAMMeta.MINI_APP_VIEW_ACTION
        )

    @patch("gcloud.core.apis.drf.viewsets.appmaker.TaskTemplate.objects.filter")
    @patch("gcloud.core.apis.drf.viewsets.appmaker.AppMaker.objects.filter")
    @patch("gcloud.core.apis.drf.viewsets.appmaker.ScopeResolver")
    def test_capabilities_are_calculated_from_authorized_resources(
        self, scope_resolver, appmaker_filter, task_template_filter
    ):
        mini_app_scope = AuthorizedScope({IAMMeta.MINI_APP_RESOURCE: {"21"}})
        flow_scope = AuthorizedScope({IAMMeta.FLOW_RESOURCE: {"31"}})
        scope_resolver.return_value.authorized_scope.side_effect = [mini_app_scope, flow_scope]
        appmaker_filter.return_value.filter.return_value.exists.return_value = True
        task_template_filter.return_value.filter.return_value.exists.return_value = False
        request = SimpleNamespace(
            user=SimpleNamespace(username="alice", tenant_id="tenant-a"),
            query_params={"project__id": "10"},
        )

        response = AppmakerListViewSet().capabilities(request)

        self.assertEqual(response.data, {"can_view": True, "can_create": False})
        appmaker_filter.assert_called_once_with(project_id="10", project__tenant_id="tenant-a", is_deleted=False)
        appmaker_filter.return_value.filter.assert_called_once_with(id__in={"21"})
        task_template_filter.assert_called_once_with(project_id="10", project__tenant_id="tenant-a", is_deleted=False)
        task_template_filter.return_value.filter.assert_called_once_with(id__in={"31"})

    @patch("gcloud.core.apis.drf.viewsets.appmaker.TaskTemplate.objects.filter")
    @patch("gcloud.core.apis.drf.viewsets.appmaker.AppMaker.objects.filter")
    @patch("gcloud.core.apis.drf.viewsets.appmaker.ScopeResolver")
    def test_project_level_scopes_enable_capabilities_without_local_children(
        self, scope_resolver, appmaker_filter, task_template_filter
    ):
        project_scope = AuthorizedScope({IAMMeta.PROJECT_RESOURCE: {"10"}})
        scope_resolver.return_value.authorized_scope.side_effect = [project_scope, project_scope]
        request = SimpleNamespace(
            user=SimpleNamespace(username="alice", tenant_id="tenant-a"),
            query_params={"project__id": "10"},
        )

        response = AppmakerListViewSet().capabilities(request)

        self.assertEqual(response.data, {"can_view": True, "can_create": True})
        appmaker_filter.assert_not_called()
        task_template_filter.assert_not_called()
