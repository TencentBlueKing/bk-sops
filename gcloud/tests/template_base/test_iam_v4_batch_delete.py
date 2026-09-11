from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.core.exceptions import FieldDoesNotExist
from django.test import SimpleTestCase
from rest_framework.exceptions import PermissionDenied

from gcloud.template_base.apis.drf.permission import CommonTemplatePermission, ProjectTemplatePermission
from gcloud.template_base.apis.drf.serilaziers.template import TemplateIdsSerializer
from gcloud.template_base.domains.template_manager import TemplateManager


class TemplateBatchDeletePermissionTestCase(SimpleTestCase):
    def request(self, template_ids):
        return SimpleNamespace(
            data={"template_ids": template_ids},
            user=SimpleNamespace(username="alice", tenant_id="tenant-a"),
        )

    def view(self):
        return SimpleNamespace(action="batch_delete", template_ids_serializer=TemplateIdsSerializer)

    def test_duplicate_ids_are_rejected(self):
        serializer = TemplateIdsSerializer(data={"template_ids": [1, 1]})
        self.assertFalse(serializer.is_valid())

    @patch("gcloud.template_base.apis.drf.permission.PermissionService")
    @patch("gcloud.template_base.apis.drf.permission.TaskTemplate.objects.select_related")
    def test_missing_or_cross_tenant_id_stops_before_iam(self, select_related, permission_service):
        select_related.return_value.filter.return_value = []

        with self.assertRaises(PermissionDenied):
            ProjectTemplatePermission().has_permission(self.request([1]), self.view())

        select_related.return_value.filter.assert_called_once_with(
            id__in=[1], is_deleted=False, project__tenant_id="tenant-a"
        )
        permission_service.assert_not_called()

    @patch("gcloud.template_base.apis.drf.permission.PermissionService")
    @patch("gcloud.template_base.apis.drf.permission.TaskTemplate.objects.select_related")
    def test_mixed_valid_and_invalid_ids_stop_before_iam(self, select_related, permission_service):
        select_related.return_value.filter.return_value = [SimpleNamespace(id=1)]

        with self.assertRaises(PermissionDenied):
            ProjectTemplatePermission().has_permission(self.request([1, 2]), self.view())

        permission_service.assert_not_called()

    @patch("gcloud.template_base.apis.drf.permission.PermissionService")
    @patch("gcloud.template_base.apis.drf.permission.CommonTemplate.objects.select_related")
    def test_common_template_invalid_id_stops_before_iam(self, select_related, permission_service):
        select_related.return_value.filter.return_value = []

        with self.assertRaises(PermissionDenied):
            CommonTemplatePermission().has_permission(self.request([99]), self.view())

        select_related.return_value.filter.assert_called_once_with(id__in=[99], is_deleted=False, tenant_id="tenant-a")
        permission_service.assert_not_called()

    @patch("gcloud.template_base.apis.drf.permission.PermissionService")
    @patch("gcloud.template_base.apis.drf.permission.TaskTemplate.objects.select_related")
    def test_verified_ids_are_bound_to_request_and_authorized(self, select_related, permission_service):
        template = SimpleNamespace(id=1, creator="alice", name="flow", project_id=10)
        select_related.return_value.filter.return_value = [template]
        request = self.request([1])

        self.assertTrue(ProjectTemplatePermission().has_permission(request, self.view()))

        self.assertEqual(request._authorized_batch_delete_template_ids, [1])
        permission_service.return_value.require_resources.assert_called_once()
        resource = permission_service.return_value.require_resources.call_args.args[3][0]
        self.assertEqual(resource.id, "1")
        self.assertEqual(resource.attribute["_bk_iam_path_"], "/project,10/")


class TemplateManagerTenantBoundaryTestCase(SimpleTestCase):
    @patch("gcloud.template_base.domains.template_manager.TemplateRelationship.objects.filter")
    def test_batch_delete_keeps_tenant_filter_in_domain_layer(self, relationship_filter):
        objects = MagicMock()
        filtered = objects.select_related.return_value.filter
        filtered.return_value = []
        model = type(
            "CommonTemplate",
            (),
            {"objects": objects, "_meta": SimpleNamespace(get_field=MagicMock())},
        )

        result = TemplateManager(model).batch_delete([1, 2], "tenant-a")

        self.assertTrue(result["result"])
        filtered.assert_called_once_with(id__in=[1, 2], is_deleted=False, tenant_id="tenant-a")
        objects.filter.assert_called_once_with(id__in=[])
        relationship_filter.assert_called_once_with(ancestor_template_id__in=[])

    @patch("gcloud.template_base.domains.template_manager.TemplateRelationship.objects.filter")
    def test_project_template_batch_delete_filters_through_project_tenant(self, unused):
        objects = MagicMock()
        filtered = objects.select_related.return_value.filter
        filtered.return_value = []
        model = type(
            "TaskTemplate",
            (),
            {
                "objects": objects,
                "_meta": SimpleNamespace(get_field=MagicMock(side_effect=FieldDoesNotExist)),
            },
        )

        TemplateManager(model).batch_delete([1], "tenant-a")

        filtered.assert_called_once_with(id__in=[1], is_deleted=False, project__tenant_id="tenant-a")
