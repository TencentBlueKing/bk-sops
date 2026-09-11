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
from gcloud.core.apis.drf.viewsets.function_task import FunctionTaskViewSet
from gcloud.core.apis.drf.viewsets.project_config import ProjectConfigViewSet
from gcloud.core.apis.drf.viewsets.resource_config import ResourceConfigViewSet
from gcloud.core.apis.drf.viewsets.staff_group import StaffGroupSetViewSet
from gcloud.core.models import Project, ResourceConfig, StaffGroupSet
from gcloud.external_plugins.models import CachePackageSource
from gcloud.iam_auth import IAMMeta, PermissionService, res_factory
from gcloud.iam_auth.exceptions import IAMPermissionDenied, IAMResourceNotFound
from gcloud.iam_auth.resource_api_v4.providers.project import ProjectResourceProvider
from gcloud.iam_auth.scope_resolver import ScopeResolver
from gcloud.iam_auth.types import AuthorizedScope
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

    def test_authorized_scope_keeps_project_descendants_as_tenant_scoped_subquery(self):
        task_t1 = TaskFlowInstance.objects.create(project=self.project_t1, current_flow="execute_task")
        TaskFlowInstance.objects.create(project=self.project_t2, current_flow="execute_task")
        client = mock.Mock()
        client.list_authorized_resources.return_value = [
            {"type": IAMMeta.PROJECT_RESOURCE, "ids": [str(self.project_t1.id)]}
        ]

        scope = ScopeResolver(client).authorized_scope("alice", "t1", IAMMeta.TASK_VIEW_ACTION)

        self.assertEqual(
            list(scope.queryset(IAMMeta.TASK_RESOURCE).values_list("id", flat=True)),
            [task_t1.id],
        )

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
