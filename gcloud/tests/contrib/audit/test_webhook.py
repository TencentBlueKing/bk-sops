# -*- coding: utf-8 -*-
from unittest import mock

from django.test import SimpleTestCase, override_settings

from gcloud.apigw.views.apply_webhook_configs import _audit_webhook_changes, _get_webhook_audit_context
from gcloud.contrib.audit.instances import AuditSnapshot


class WebhookAuditTestCase(SimpleTestCase):
    @mock.patch("gcloud.apigw.views.apply_webhook_configs.bk_audit_add_event_on_commit")
    def test_webhook_audit_only_contains_safe_summary(self, add_event):
        template = mock.Mock(id=101)
        origins = {"101": AuditSnapshot({"template_id": 101, "webhook_enabled": False, "event_types": []})}

        _audit_webhook_changes(
            username="admin",
            templates={"101": template},
            origins=origins,
            enabled=True,
            events_by_template={"101": ["task_finished"]},
        )

        event_data = add_event.call_args[1]["data"]
        self.assertEqual(
            event_data,
            {
                "template_id": 101,
                "webhook_enabled": True,
                "event_types": ["task_finished"],
            },
        )
        self.assertNotIn("endpoint", event_data)
        self.assertNotIn("headers", event_data)
        self.assertNotIn("extra_info", event_data)

    @override_settings(ENABLE_BK_AUDIT=False)
    @mock.patch("gcloud.apigw.views.apply_webhook_configs.TaskTemplate.objects.filter")
    def test_disabled_webhook_audit_does_not_query(self, template_filter):
        self.assertEqual(_get_webhook_audit_context(1, [101]), ({}, {}))
        template_filter.assert_not_called()

    @override_settings(ENABLE_BK_AUDIT=True)
    @mock.patch(
        "gcloud.apigw.views.apply_webhook_configs.TaskTemplate.objects.filter",
        side_effect=RuntimeError("audit query failed"),
    )
    def test_webhook_audit_query_error_does_not_affect_business(self, template_filter):
        self.assertEqual(_get_webhook_audit_context(1, [101]), ({}, {}))
