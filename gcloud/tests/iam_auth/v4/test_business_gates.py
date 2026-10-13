from types import SimpleNamespace
from unittest import mock

import ujson as json
from django.core.cache import cache
from django.test import TestCase
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied

from gcloud.analysis_statistics.service import effective_time_for_task
from gcloud.contrib.function.models import FunctionTask
from gcloud.core.apis.drf.exceptions import ObjectDoesNotExistException
from gcloud.core.apis.drf.serilaziers.taskflow_instance import CreateTaskFlowInstanceSerializer
from gcloud.core.apis.drf.viewsets.appmaker import AppmakerListViewSet
from gcloud.core.apis.drf.viewsets.function_task import FunctionTaskViewSet
from gcloud.core.apis.drf.viewsets.project_config import ProjectConfigViewSet
from gcloud.core.apis.drf.viewsets.resource_config import ResourceConfigViewSet
from gcloud.core.apis.drf.viewsets.staff_group import StaffGroupSetViewSet
from gcloud.core.models import Project, ResourceConfig, StaffGroupSet
from gcloud.external_plugins.models import CachePackageSource
from gcloud.iam_auth import IAMMeta, PermissionCheck, PermissionService, res_factory
from gcloud.iam_auth.exceptions import IAMPermissionDenied, IAMResourceNotFound
from gcloud.iam_auth.resource_api_v4.providers.project import ProjectResourceProvider
from gcloud.iam_auth.scope_resolver import ScopeResolver
from gcloud.iam_auth.types import AuthorizedScope
from gcloud.iam_auth.view_interceptors.apigw.functionalization_task_view import FunctionViewInterceptor
from gcloud.iam_auth.view_interceptors.taskflow import BatchStatusViewInterceptor
from gcloud.taskflow3.models import TaskFlowInstance


def request_for(tenant_id, data=None):
    return SimpleNamespace(
        user=SimpleNamespace(username="alice", tenant_id=tenant_id),
        data=data or {},
        query_params={},
    )


class TenantBoundaryDatabaseTest(TestCase):
    def setUp(self):
        self.project_t1 = Project.objects.create(name="tenant-one", creator="alice", bk_biz_id=91001, tenant_id="t1")
        self.project_t2 = Project.objects.create(name="tenant-two", creator="bob", bk_biz_id=91002, tenant_id="t2")

    def test_f02_resource_factory_accepts_owner_tenant_and_rejects_other_tenant(self):
        self.assertEqual(res_factory.resources_for_project(self.project_t1.id, "t1")[0].id, str(self.project_t1.id))
        self.assertEqual(res_factory.resources_for_project(self.project_t1.id, "t2"), [])

    def test_f02_effective_time_project_lookup_is_tenant_scoped(self):
        denied = effective_time_for_task("project", 999999, self.project_t1.id, "t2")
        allowed_project = effective_time_for_task("project", 999999, self.project_t1.id, "t1")
        self.assertIn("project", denied["message"])
        self.assertIn("task", allowed_project["message"])

    def test_f02_write_serializer_and_project_config_reject_cross_tenant_project(self):
        serializer = CreateTaskFlowInstanceSerializer(context={"request": request_for("t1")})
        self.assertEqual(serializer.validate_project(self.project_t1.id), self.project_t1)
        with self.assertRaises(serializers.ValidationError):
            serializer.validate_project(self.project_t2.id)

        view = ProjectConfigViewSet()
        view.request = request_for("t1")
        view.kwargs = {"pk": self.project_t2.id}
        with self.assertRaises(ObjectDoesNotExistException):
            view.get_object()

    def test_f03_package_sources_are_isolated_by_tenant(self):
        own = CachePackageSource.objects.create(type="git", tenant_id="t1")
        CachePackageSource.objects.create(type="git", tenant_id="t2")
        from gcloud.core.apis.drf.viewsets.package_source import get_all_source_objects

        visible_ids = {item.id for item in get_all_source_objects("t1") if isinstance(item, CachePackageSource)}
        self.assertEqual(visible_ids, {own.id})

    def test_f04_callback_count_and_page_are_tenant_scoped(self):
        cache.clear()
        Project.objects.create(name="tenant-one-b", creator="alice", bk_biz_id=91003, tenant_id="t1")
        result = ProjectResourceProvider().list_instance("t1", page=1, page_size=1)
        self.assertEqual(result["count"], 2)
        self.assertEqual(len(result["results"]), 1)
        self.assertNotIn(str(self.project_t2.id), {item["id"] for item in result["results"]})

    def test_f05_resource_config_queryset_hides_other_tenant(self):
        own = ResourceConfig.objects.create(
            project_id=self.project_t1.id, name="own", config_type="host", creator="alice"
        )
        ResourceConfig.objects.create(project_id=self.project_t2.id, name="other", config_type="host", creator="bob")
        view = ResourceConfigViewSet()
        view.request = request_for("t1")
        self.assertEqual(list(view.get_queryset().values_list("id", flat=True)), [own.id])

    def test_f10_staff_group_create_authorizes_before_database_write(self):
        request = request_for("t1", {"project_id": self.project_t1.id, "name": "operators", "members": "alice"})
        view = StaffGroupSetViewSet()
        with mock.patch.object(view, "iam_auth_check", side_effect=PermissionDenied):
            with self.assertRaises(PermissionDenied):
                view.create(request)
        self.assertFalse(StaffGroupSet.objects.filter(project_id=self.project_t1.id).exists())

        with mock.patch.object(view, "iam_auth_check") as auth:
            response = view.create(request)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(StaffGroupSet.objects.filter(project_id=self.project_t1.id, name="operators").exists())
        self.assertEqual(auth.call_args.kwargs["action"], IAMMeta.PROJECT_EDIT_ACTION)

    def test_f10_staff_group_queryset_rejects_cross_tenant_object(self):
        own = StaffGroupSet.objects.create(project_id=self.project_t1.id, name="own")
        StaffGroupSet.objects.create(project_id=self.project_t2.id, name="other")
        view = StaffGroupSetViewSet()
        view.request = request_for("t1")
        self.assertEqual(list(view.get_queryset().values_list("id", flat=True)), [own.id])

    def test_f07_function_task_exact_filter_limits_scope_candidates(self):
        task = TaskFlowInstance.objects.create(project=self.project_t1, current_flow="func_claim")
        FunctionTask.objects.create(task=task, creator="alice")
        other_task = TaskFlowInstance.objects.create(project=self.project_t2, current_flow="func_claim")
        FunctionTask.objects.create(task=other_task, creator="bob")
        view = FunctionTaskViewSet()
        view.action = "list"
        view.request = request_for("t1")
        view.request.query_params = {"task_id": str(task.id), "task__project__id": str(self.project_t1.id)}
        scopes = {
            IAMMeta.FUNCTION_TASK_VIEW_ACTION: AuthorizedScope(
                values={IAMMeta.PROJECT_RESOURCE: {str(self.project_t1.id)}}
            ),
            IAMMeta.TASK_VIEW_ACTION: AuthorizedScope(values={IAMMeta.TASK_RESOURCE: {str(task.id)}}),
        }
        with mock.patch(
            "gcloud.core.apis.drf.viewsets.function_task.ScopeResolver.authorized_scope",
            side_effect=lambda username, tenant_id, action_id, **kwargs: scopes[action_id],
        ) as authorize:
            self.assertEqual(list(view.get_queryset().values_list("task_id", flat=True)), [task.id])

        task_call = authorize.call_args_list[1]
        self.assertEqual(task_call.kwargs["project_id"], str(self.project_t1.id))
        self.assertEqual(list(task_call.kwargs["resource_ids"]), [task.id])

    def test_f07_gateway_list_passes_validated_project_and_task_candidates(self):
        request = request_for("t1")
        request.is_trust = False
        request.GET = {"project_id": str(self.project_t1.id), "task_id_in": "11,12"}
        scopes = {
            IAMMeta.FUNCTION_TASK_VIEW_ACTION: AuthorizedScope(
                values={IAMMeta.PROJECT_RESOURCE: {str(self.project_t1.id)}}
            ),
            IAMMeta.TASK_VIEW_ACTION: AuthorizedScope(values={IAMMeta.TASK_RESOURCE: {"11"}}),
        }
        with mock.patch(
            "gcloud.iam_auth.view_interceptors.apigw.functionalization_task_view.ScopeResolver.authorized_scope",
            side_effect=lambda username, tenant_id, action_id, **kwargs: scopes[action_id],
        ) as authorize:
            FunctionViewInterceptor().process(request)

        self.assertEqual(request._function_task_ids, frozenset({"11"}))
        self.assertEqual(
            authorize.call_args_list[1].kwargs,
            {"project_id": self.project_t1.id, "resource_ids": ["11", "12"]},
        )

    def test_f07_gateway_function_task_ids_only_probe_tenant_local_tasks(self):
        task = TaskFlowInstance.objects.create(project=self.project_t1, current_flow="func_claim")
        selected = FunctionTask.objects.create(task=task, creator="alice")
        foreign_task = TaskFlowInstance.objects.create(project=self.project_t2, current_flow="func_claim")
        foreign = FunctionTask.objects.create(task=foreign_task, creator="bob")
        request = request_for("t1")
        request.is_trust = False
        request.GET = {"id_in": "{},{}".format(selected.id, foreign.id)}
        scopes = {
            IAMMeta.FUNCTION_TASK_VIEW_ACTION: AuthorizedScope(
                values={IAMMeta.PROJECT_RESOURCE: {str(self.project_t1.id)}}
            ),
            IAMMeta.TASK_VIEW_ACTION: AuthorizedScope(values={IAMMeta.TASK_RESOURCE: {str(task.id)}}),
        }
        with mock.patch(
            "gcloud.iam_auth.view_interceptors.apigw.functionalization_task_view.ScopeResolver.authorized_scope",
            side_effect=lambda username, tenant_id, action_id, **kwargs: scopes[action_id],
        ) as authorize:
            FunctionViewInterceptor().process(request)

        self.assertEqual(list(authorize.call_args_list[1].kwargs["resource_ids"]), [task.id])

    def test_f07_function_task_list_intersects_project_task_and_tenant_scopes(self):
        task_t1 = TaskFlowInstance.objects.create(project=self.project_t1, current_flow="func_claim")
        task_t2 = TaskFlowInstance.objects.create(project=self.project_t2, current_flow="func_claim")
        own = FunctionTask.objects.create(task=task_t1, creator="alice")
        FunctionTask.objects.create(task=task_t2, creator="bob")
        view = FunctionTaskViewSet()
        view.action = "list"
        view.request = request_for("t1")

        scopes = {
            IAMMeta.FUNCTION_TASK_VIEW_ACTION: AuthorizedScope(
                values={IAMMeta.PROJECT_RESOURCE: {str(self.project_t1.id)}}
            ),
            IAMMeta.TASK_VIEW_ACTION: AuthorizedScope(
                values={IAMMeta.TASK_RESOURCE: {str(task_t1.id), str(task_t2.id)}}
            ),
        }
        with mock.patch(
            "gcloud.core.apis.drf.viewsets.function_task.ScopeResolver.authorized_scope",
            side_effect=lambda username, tenant_id, action_id: scopes[action_id],
        ):
            self.assertEqual(list(view.get_queryset().values_list("id", flat=True)), [own.id])

        scopes[IAMMeta.TASK_VIEW_ACTION] = AuthorizedScope(values={IAMMeta.TASK_RESOURCE: set()})
        with mock.patch(
            "gcloud.core.apis.drf.viewsets.function_task.ScopeResolver.authorized_scope",
            side_effect=lambda username, tenant_id, action_id: scopes[action_id],
        ):
            self.assertFalse(view.get_queryset().exists())

    def test_authorized_scope_checks_project_ancestor_without_child_list_endpoint(self):
        task_t1 = TaskFlowInstance.objects.create(project=self.project_t1, current_flow="execute_task")
        TaskFlowInstance.objects.create(project=self.project_t2, current_flow="execute_task")
        client = mock.Mock()
        probe_id = "__sops_project_scope_{}__".format(self.project_t1.id)
        client.direct_auth_by_resources.return_value = {probe_id: True}

        scope = ScopeResolver(client).authorized_scope("alice", "t1", IAMMeta.TASK_VIEW_ACTION)

        self.assertEqual(
            list(scope.queryset(IAMMeta.TASK_RESOURCE).values_list("id", flat=True)),
            [task_t1.id],
        )
        self.assertTrue(scope.contains(IAMMeta.PROJECT_RESOURCE, self.project_t1.id))
        client.list_authorized_resources.assert_not_called()
        probe = client.direct_auth_by_resources.call_args.args[3][0]
        self.assertEqual(probe.attribute["_bk_iam_path_"], "/project,{}/".format(self.project_t1.id))

    def test_authorized_scope_includes_granular_child_grants_outside_project_scope(self):
        another_project = Project.objects.create(name="tenant-one-b", creator="bob", bk_biz_id=91003, tenant_id="t1")
        allowed_task = TaskFlowInstance.objects.create(project=self.project_t1, current_flow="execute_task")
        TaskFlowInstance.objects.create(project=another_project, current_flow="execute_task")
        foreign_task = TaskFlowInstance.objects.create(project=self.project_t2, current_flow="execute_task")
        client = mock.Mock()
        client.direct_auth_by_resources.side_effect = lambda tenant_id, subject, action_id, resources: {
            resource.id: resource.id == str(allowed_task.id) for resource in resources
        }

        scope = ScopeResolver(client).authorized_scope("alice", "t1", IAMMeta.TASK_VIEW_ACTION)

        self.assertEqual(list(scope.queryset(IAMMeta.TASK_RESOURCE).values_list("id", flat=True)), [allowed_task.id])
        self.assertFalse(scope.contains(IAMMeta.PROJECT_RESOURCE, self.project_t1.id))
        self.assertFalse(scope.queryset(IAMMeta.TASK_RESOURCE).filter(id=foreign_task.id).exists())
        client.list_authorized_resources.assert_not_called()
        for call in client.direct_auth_by_resources.call_args_list:
            self.assertEqual(call.args[0], "t1")
            for resource in call.args[3]:
                self.assertNotEqual(resource.attribute["_bk_iam_path_"], "/project,{}/".format(self.project_t2.id))

    def test_child_scope_limits_iam_checks_to_requested_candidates(self):
        another_project = Project.objects.create(name="tenant-one-b", creator="bob", bk_biz_id=91003, tenant_id="t1")
        selected = TaskFlowInstance.objects.create(project=self.project_t1, current_flow="execute_task")
        other = TaskFlowInstance.objects.create(project=another_project, current_flow="execute_task")
        foreign = TaskFlowInstance.objects.create(project=self.project_t2, current_flow="execute_task")
        probe_id = "__sops_project_scope_{}__".format(self.project_t1.id)
        client = mock.Mock()
        grant_id = probe_id
        client.direct_auth_by_resources.side_effect = lambda tenant_id, subject, action_id, resources: {
            resource.id: resource.id == grant_id for resource in resources
        }

        scope = ScopeResolver(client).authorized_scope(
            "alice", "t1", IAMMeta.TASK_VIEW_ACTION, include_creator=False, project_id=self.project_t1.id
        )
        self.assertEqual(list(scope.queryset(IAMMeta.TASK_RESOURCE).values_list("id", flat=True)), [selected.id])
        self.assertEqual(client.direct_auth_by_resources.call_count, 1)
        self.assertEqual([item.id for item in client.direct_auth_by_resources.call_args.args[3]], [probe_id])

        client.reset_mock()
        grant_id = str(selected.id)
        scope = ScopeResolver(client).authorized_scope(
            "alice", "t1", IAMMeta.TASK_VIEW_ACTION, include_creator=False, resource_ids=[selected.id]
        )
        self.assertEqual(list(scope.queryset(IAMMeta.TASK_RESOURCE).values_list("id", flat=True)), [selected.id])
        checked_ids = [item.id for call in client.direct_auth_by_resources.call_args_list for item in call.args[3]]
        self.assertEqual(checked_ids, [str(selected.id)])
        self.assertNotIn(str(other.id), checked_ids)
        self.assertNotIn(str(foreign.id), checked_ids)

        client.reset_mock()
        scope = ScopeResolver(client).authorized_scope(
            "alice", "t1", IAMMeta.TASK_VIEW_ACTION, include_creator=False, resource_ids=[foreign.id]
        )
        self.assertIsNone(scope.queryset(IAMMeta.TASK_RESOURCE))
        client.direct_auth_by_resources.assert_not_called()

    @mock.patch("gcloud.iam_auth.scope_resolver.IAMV4Client")
    def test_appmaker_capabilities_accept_project_scoped_child_actions(self, client_class):
        Project.objects.create(name="tenant-one-b", creator="bob", bk_biz_id=91003, tenant_id="t1")
        client = client_class.return_value
        client.direct_auth_by_resources.side_effect = lambda tenant_id, subject, action_id, resources: {
            resource.id: True for resource in resources
        }
        request = request_for("t1")
        request.query_params = {"project__id": str(self.project_t1.id)}

        response = AppmakerListViewSet().capabilities(request)

        self.assertEqual(response.data, {"can_view": True, "can_create": True})
        self.assertEqual(
            [call.args[2] for call in client.direct_auth_by_resources.call_args_list],
            [IAMMeta.MINI_APP_VIEW_ACTION, IAMMeta.FLOW_CREATE_MINI_APP_ACTION],
        )
        client.list_authorized_resources.assert_not_called()
        for call in client.direct_auth_by_resources.call_args_list:
            self.assertEqual(len(call.args[3]), 1)
            self.assertEqual(call.args[3][0].attribute["_bk_iam_path_"], "/project,{}/".format(self.project_t1.id))

    def test_child_detail_does_not_use_unsupported_scope_endpoint(self):
        task_t1 = TaskFlowInstance.objects.create(project=self.project_t1, current_flow="execute_task")
        client = mock.Mock()
        client.direct_auth.return_value = False
        client.list_authorized_resources.return_value = [
            {"type": IAMMeta.PROJECT_RESOURCE, "ids": [str(self.project_t1.id)]}
        ]

        allowed = PermissionService(client).is_allowed(
            "bob",
            "t1",
            PermissionCheck(IAMMeta.TASK_VIEW_ACTION, res_factory.resources_for_task(task_t1.id, "t1")[0]),
        )

        self.assertFalse(allowed)
        client.list_authorized_resources.assert_not_called()

    def test_resource_action_matrix_uses_one_local_query_for_all_actions(self):
        project_t1_b = Project.objects.create(
            name="tenant-one-b",
            creator="alice",
            bk_biz_id=91003,
            tenant_id="t1",
        )
        resources = [
            res_factory.resources_for_project_obj(self.project_t1)[0],
            res_factory.resources_for_project_obj(project_t1_b)[0],
        ]
        client = mock.Mock()
        client.direct_auth_by_resources.side_effect = lambda tenant_id, subject, action_id, items: {
            str(item.id): True for item in items
        }

        with self.assertNumQueries(1):
            result = PermissionService(client).allowed_resource_actions(
                "bob",
                "t1",
                [IAMMeta.PROJECT_VIEW_ACTION, IAMMeta.PROJECT_EDIT_ACTION],
                resources,
            )

        self.assertTrue(all(all(actions.values()) for actions in result.values()))

    def test_f09_batch_status_checks_real_tenant_tasks_and_rejects_denied_or_cross_tenant(self):
        task_t1 = TaskFlowInstance.objects.create(project=self.project_t1, current_flow="execute_task")
        task_t2 = TaskFlowInstance.objects.create(project=self.project_t2, current_flow="execute_task")
        request = request_for("t1")
        request.body = json.dumps({"task_ids": [task_t1.id]}).encode()

        with mock.patch(
            "gcloud.iam_auth.view_interceptors.taskflow.PermissionService.allowed_resources",
            return_value={str(task_t1.id): True},
        ):
            self.assertIsNone(BatchStatusViewInterceptor().process(request))

        with mock.patch(
            "gcloud.iam_auth.view_interceptors.taskflow.PermissionService.allowed_resources",
            return_value={str(task_t1.id): False},
        ):
            with self.assertRaises(IAMPermissionDenied):
                BatchStatusViewInterceptor().process(request)

        request.body = json.dumps({"task_ids": [task_t2.id]}).encode()
        with self.assertRaises(IAMResourceNotFound):
            BatchStatusViewInterceptor().process(request)
