from types import SimpleNamespace
from unittest import mock

from django.test import SimpleTestCase
from rest_framework.exceptions import PermissionDenied

from gcloud.contrib.operate_record.apis.drf.serilaziers.operate_record import TaskOperateRecordSetSerializer
from gcloud.contrib.operate_record.apis.drf.viewsets.operate_record import (
    TaskOperateRecordSetPermission,
    TaskOperateRecordSetViewSet,
)

# Load the shared ViewSet package in the same order as the project URLConf.  The
# legacy permission module imports viewsets.utils through the package and is
# otherwise sensitive to being the first DRF module imported in a test process.
from gcloud.core.apis.drf import viewsets as _viewsets  # noqa: F401
from gcloud.iam_auth import IAMMeta


class TaskOperateRecordViewTest(SimpleTestCase):
    def request(self, project_id="1", instance_id="409"):
        return SimpleNamespace(
            query_params={"project_id": project_id, "instance_id": instance_id, "node_id": "node-1"},
            user=SimpleNamespace(tenant_id="tenant-a", username="auditor"),
        )

    def test_permission_checks_task_instead_of_active_project(self):
        permission_info = TaskOperateRecordSetPermission.actions["list"]

        self.assertEqual(permission_info.iam_action, IAMMeta.TASK_VIEW_ACTION)
        self.assertEqual(permission_info.id_field, "instance_id")

    def test_task_serializer_does_not_apply_active_project_validator(self):
        serializer = TaskOperateRecordSetSerializer(data={"project_id": 1, "instance_id": 409})

        self.assertTrue(serializer.is_valid(), serializer.errors)

    @mock.patch("gcloud.contrib.operate_record.apis.drf.viewsets.operate_record.TaskFlowInstance.objects.filter")
    def test_list_uses_real_tenant_task(self, task_filter):
        request = self.request()
        task_filter.return_value.first.return_value = SimpleNamespace(
            project_id=1, project=SimpleNamespace(tenant_id="tenant-a")
        )
        queryset = mock.Mock()
        queryset.filter.return_value = []
        view = TaskOperateRecordSetViewSet()
        view.action = "list"
        view.request = request
        view.get_queryset = mock.Mock(return_value=queryset)
        view.get_serializer = mock.Mock(return_value=SimpleNamespace(data=[{"operator": "opaque-user"}]))

        response = view.list(request)

        self.assertEqual(response.data, [{"operator": "opaque-user"}])
        task_filter.assert_called_once_with(id=409, project__tenant_id="tenant-a")
        queryset.filter.assert_called_once_with(project_id=1, instance_id=409, node_id="node-1")

    @mock.patch("gcloud.contrib.operate_record.apis.drf.viewsets.operate_record.TaskFlowInstance.objects.filter")
    def test_list_rejects_forged_project_id(self, task_filter):
        request = self.request(project_id="2")
        task_filter.return_value.first.return_value = SimpleNamespace(project_id=1)
        view = TaskOperateRecordSetViewSet()
        view.action = "list"
        view.request = request

        with self.assertRaises(PermissionDenied):
            view.list(request)
