# -*- coding: utf-8 -*-
from unittest import mock

from django.test import SimpleTestCase, override_settings

from gcloud.contrib.audit import operations


@override_settings(ENABLE_BK_AUDIT=True)
class AuditOperationsTestCase(SimpleTestCase):
    @mock.patch("gcloud.contrib.audit.operations.bk_audit_add_event_on_commit")
    @mock.patch(
        "gcloud.contrib.audit.operations.get_template_audit_meta",
        return_value=("flow_create", "flow_delete", "flow"),
    )
    def test_import_only_reports_real_result_ids(self, get_meta, add_event):
        instances = [mock.Mock(id=101), mock.Mock(id=102)]
        model_cls = mock.Mock()
        model_cls.objects.filter.return_value = instances
        result = {"result": True, "data": {"flows": {"101": "a", "102": "b"}}}

        operations.audit_imported_templates("admin", model_cls, result)

        model_cls.objects.filter.assert_called_once_with(id__in=[101, 102])
        self.assertEqual(add_event.call_count, 2)
        self.assertEqual({call[1]["instance"].id for call in add_event.call_args_list}, {101, 102})

    @mock.patch("gcloud.contrib.audit.operations.bk_audit_add_event_on_commit")
    def test_failed_import_reports_nothing(self, add_event):
        operations.audit_imported_templates("admin", mock.Mock(), {"result": False, "data": None})

        add_event.assert_not_called()

    @override_settings(ENABLE_BK_AUDIT=False)
    @mock.patch("gcloud.contrib.audit.operations.get_template_audit_meta")
    def test_disabled_import_does_not_build_mapping_or_query(self, get_meta):
        model_cls = mock.Mock()

        operations.audit_imported_templates("admin", model_cls, {"result": True, "data": {"flows": {"101": "flow"}}})

        get_meta.assert_not_called()
        model_cls.objects.filter.assert_not_called()

    @mock.patch("gcloud.contrib.audit.operations.bk_audit_add_event_on_commit")
    @mock.patch(
        "gcloud.contrib.audit.operations.get_template_audit_meta",
        return_value=("flow_create", "flow_delete", "flow"),
    )
    def test_import_audit_query_error_does_not_affect_business(self, get_meta, add_event):
        model_cls = mock.Mock()
        model_cls.objects.filter.side_effect = RuntimeError("audit query failed")

        operations.audit_imported_templates("admin", model_cls, {"result": True, "data": {"flows": {"101": "flow"}}})

        add_event.assert_not_called()

    @mock.patch("gcloud.contrib.audit.operations.get_audit_snapshot", return_value={"id": 101})
    @mock.patch("gcloud.contrib.audit.operations.bk_audit_add_event_on_commit")
    @mock.patch(
        "gcloud.contrib.audit.operations.get_template_audit_meta",
        return_value=("flow_create", "flow_delete", "flow"),
    )
    def test_delete_only_reports_success_ids(self, get_meta, add_event, get_snapshot):
        success = mock.Mock(id=101)
        failed = mock.Mock(id=102)

        operations.audit_deleted_templates(
            username="admin",
            template_model_cls=mock.Mock(),
            instances_by_id={101: success, 102: failed},
            success_ids=["101"],
        )

        add_event.assert_called_once()
        self.assertEqual(add_event.call_args[1]["instance"], success)
        self.assertEqual(add_event.call_args[1]["data"], {"id": 101, "is_deleted": True})
