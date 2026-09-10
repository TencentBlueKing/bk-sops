from types import SimpleNamespace
from unittest.mock import patch

from django.test import SimpleTestCase

from gcloud.clocked_task.permissions import ClockedTaskPermissions
from gcloud.core.apis.drf.viewsets.periodic_task import PeriodicTaskPermission
from gcloud.core.apis.drf.viewsets.taskflow import TaskFlowInstancePermission


def _template(creator="creator"):
    return SimpleNamespace(id=1, pipeline_template=SimpleNamespace(creator=creator))


def _request(data):
    return SimpleNamespace(
        data=data,
        query_params={},
        user=SimpleNamespace(username="creator", tenant_id="system"),
    )


class IAMV4FlowCreatorCreatePermissionTestCase(SimpleTestCase):
    def test_creator_can_create_task_from_own_flow_without_remote_creator_grant(self):
        request = _request({"template": 1, "template_source": "project", "project": 10})
        view = SimpleNamespace(action="create")

        with patch("gcloud.core.apis.drf.viewsets.taskflow.TaskTemplate.objects.get", return_value=_template()):
            with patch.object(TaskFlowInstancePermission, "iam_auth_check") as iam_auth_check:
                self.assertTrue(TaskFlowInstancePermission().has_permission(request, view))

        iam_auth_check.assert_not_called()

    def test_creator_can_create_periodic_task_from_own_flow_without_remote_creator_grant(self):
        request = _request({"template_id": 1, "template_source": "project", "project": 10})
        view = SimpleNamespace(action="create")
        queryset = SimpleNamespace(first=lambda: _template())

        with patch("gcloud.core.apis.drf.viewsets.periodic_task.TaskTemplate.objects.filter", return_value=queryset):
            with patch.object(PeriodicTaskPermission, "iam_auth_check") as iam_auth_check:
                self.assertTrue(PeriodicTaskPermission().has_permission(request, view))

        iam_auth_check.assert_not_called()

    def test_creator_can_create_clocked_task_from_own_flow_without_remote_creator_grant(self):
        request = _request({"template_id": 1, "project_id": 10})
        queryset = SimpleNamespace(first=lambda: _template())

        class Serializer:
            def __init__(self, data):
                self.validated_data = {
                    "template_id": data["template_id"],
                    "project_id": data["project_id"],
                }

            def is_valid(self, raise_exception=False):
                return True

        view = SimpleNamespace(action="create", serializer_class=Serializer)
        with patch("gcloud.clocked_task.permissions.TaskTemplate.objects.filter", return_value=queryset):
            with patch.object(ClockedTaskPermissions, "iam_auth_check") as iam_auth_check:
                self.assertTrue(ClockedTaskPermissions().has_permission(request, view))

        iam_auth_check.assert_not_called()
