from types import SimpleNamespace
from unittest.mock import patch

from django.test import SimpleTestCase
from rest_framework import serializers

from gcloud.apigw.views.create_clocked_task import build_clocked_task_params
from gcloud.constants import PROJECT, TaskCreateMethod
from gcloud.core.apis.drf.serilaziers.taskflow_instance import CreateTaskFlowInstanceSerializer
from gcloud.core.apis.drf.viewsets.taskflow import TaskFlowInstancePermission


class ClockedTaskRouteBindingTestCase(SimpleTestCase):
    def test_body_cannot_override_route_bound_fields(self):
        template = SimpleNamespace(id=7, name="authorized-flow")
        project = SimpleNamespace(id=9)

        params = build_clocked_task_params(
            template,
            project,
            {
                "template_id": 999,
                "project_id": 888,
                "template_name": "forged-flow",
                "template_source": "common",
                "task_name": "new task",
            },
        )

        self.assertEqual(params["template_id"], 7)
        self.assertEqual(params["project_id"], 9)
        self.assertEqual(params["template_name"], "authorized-flow")
        self.assertEqual(params["template_source"], PROJECT)
        self.assertEqual(params["task_name"], "new task")


class MiniAppTaskBindingTestCase(SimpleTestCase):
    def request(self, project=10, template=20, template_source="project"):
        return SimpleNamespace(
            data={
                "create_method": TaskCreateMethod.APP_MAKER.value,
                "create_info": 30,
                "project": project,
                "template": template,
                "template_source": template_source,
            },
            query_params={},
            user=SimpleNamespace(username="alice", tenant_id="tenant-a"),
        )

    @patch("gcloud.core.apis.drf.viewsets.taskflow.AppMaker.objects.get")
    def test_permission_rejects_project_or_template_swapping(self, get_app_maker):
        get_app_maker.return_value = SimpleNamespace(id=30, project_id=10, task_template_id=20)
        permission = TaskFlowInstancePermission()

        with patch.object(permission, "iam_auth_check") as iam_auth_check:
            self.assertFalse(permission.has_permission(self.request(project=11), SimpleNamespace(action="create")))
            self.assertFalse(permission.has_permission(self.request(template=21), SimpleNamespace(action="create")))
            self.assertFalse(
                permission.has_permission(
                    self.request(template_source="common"),
                    SimpleNamespace(action="create"),
                )
            )

        iam_auth_check.assert_not_called()

    @patch("gcloud.core.apis.drf.viewsets.taskflow.AppMaker.objects.get")
    def test_permission_authorizes_the_bound_mini_app(self, get_app_maker):
        app_maker = SimpleNamespace(id=30, project_id=10, task_template_id=20, creator="alice", name="mini-app")
        get_app_maker.return_value = app_maker
        permission = TaskFlowInstancePermission()

        with patch.object(permission, "iam_auth_check") as iam_auth_check:
            self.assertTrue(permission.has_permission(self.request(), SimpleNamespace(action="create")))

        iam_auth_check.assert_called_once()

    def test_serializer_rejects_mini_app_binding_mismatch(self):
        serializer = CreateTaskFlowInstanceSerializer()
        serializer._app_maker = SimpleNamespace(project_id=10, task_template_id=20)
        attrs = {
            "create_method": TaskCreateMethod.APP_MAKER.value,
            "project": SimpleNamespace(id=10),
            "template": SimpleNamespace(id=21),
            "template_source": "project",
        }

        with self.assertRaisesRegex(serializers.ValidationError, "轻应用关联的项目或流程不匹配"):
            serializer.validate(attrs)
