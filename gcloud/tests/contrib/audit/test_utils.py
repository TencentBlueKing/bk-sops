# -*- coding: utf-8 -*-
import json
from unittest import mock

from django.db import transaction
from django.test import SimpleTestCase, TestCase, override_settings

from gcloud.contrib.audit import utils


class AuditUtilsTestCase(SimpleTestCase):
    @override_settings(ENABLE_BK_AUDIT=False)
    @mock.patch("gcloud.contrib.audit.utils.transaction.on_commit")
    def test_disabled_event_does_not_register_callback(self, on_commit):
        utils.bk_audit_add_event_on_commit(
            username="admin", action_id="task_edit", resource_id="task", instance=mock.Mock(id=1)
        )

        on_commit.assert_not_called()

    @override_settings(ENABLE_BK_AUDIT=True)
    @mock.patch("gcloud.contrib.audit.utils.transaction.on_commit")
    def test_enabled_event_registers_callback(self, on_commit):
        utils.bk_audit_add_event_on_commit(
            username="admin", action_id="task_edit", resource_id="task", instance=mock.Mock(id=1)
        )

        on_commit.assert_called_once()

    def test_sanitize_audit_data_removes_sensitive_and_large_fields(self):
        data = {
            "name": "task",
            "token": "secret-token",
            "nested": {"password": "secret-password", "safe": "value"},
            "pipeline_tree": {"activities": {"node": {}}},
            "constants": {"${password}": {"value": "secret-value"}},
            "headers": {"Authorization": "Bearer secret"},
        }

        sanitized = utils.sanitize_audit_data(data)

        self.assertEqual(sanitized["name"], "task")
        self.assertEqual(sanitized["token"], "******")
        self.assertEqual(sanitized["nested"]["password"], "******")
        self.assertEqual(sanitized["nested"]["safe"], "value")
        self.assertNotIn("pipeline_tree", sanitized)
        self.assertNotIn("constants", sanitized)
        self.assertNotIn("headers", sanitized)

    def test_sanitize_audit_data_redacts_nested_json_strings(self):
        data = {
            "notify_receivers": json.dumps(
                {
                    "receiver_group": ["Maintainers"],
                    "extra_info": {"token": "secret-token"},
                    "webhook_secret": "secret-value",
                }
            )
        }

        sanitized = json.loads(utils.sanitize_audit_data(data)["notify_receivers"])

        self.assertEqual(sanitized["receiver_group"], ["Maintainers"])
        self.assertNotIn("extra_info", sanitized)
        self.assertEqual(sanitized["webhook_secret"], "******")

    @override_settings(ENABLE_BK_AUDIT=True)
    @mock.patch("gcloud.contrib.audit.utils.build_instance", side_effect=RuntimeError("sdk failed"))
    def test_client_error_isolated_and_logged_without_instance_body(self, build_instance):
        instance = mock.Mock(id=1)
        instance.__str__ = mock.Mock(return_value="secret-instance-body")

        with self.assertLogs("root", level="ERROR") as logs:
            utils.bk_audit_add_event("admin", "task_edit", "task", instance)

        output = "\n".join(logs.output)
        self.assertIn("bk_audit_add_event_failed", output)
        self.assertIn("action_id=task_edit", output)
        self.assertIn("resource_id=task", output)
        self.assertIn("instance_id=1", output)
        self.assertNotIn("secret-instance-body", output)

    @override_settings(ENABLE_BK_AUDIT=True)
    @mock.patch("gcloud.contrib.audit.utils.bk_audit_client.add_event")
    @mock.patch("gcloud.contrib.audit.utils.build_instance", return_value="audit-instance")
    def test_event_sanitizes_origin_and_current_data(self, build_instance, add_event):
        instance = mock.Mock(id=1)

        utils.bk_audit_add_event(
            "admin",
            "task_edit",
            "task",
            instance,
            origin_data={"password": "origin-secret", "name": "old"},
            data={"token": "current-secret", "name": "new", "pipeline_tree": {"activities": {}}},
        )

        origin_data = build_instance.call_args[0][2]
        current_data = build_instance.call_args[0][3]
        self.assertEqual(origin_data, {"password": "******", "name": "old"})
        self.assertEqual(current_data, {"token": "******", "name": "new"})
        add_event.assert_called_once()


class AuditTransactionTestCase(TestCase):
    @override_settings(ENABLE_BK_AUDIT=True)
    @mock.patch("gcloud.contrib.audit.utils.bk_audit_add_event")
    def test_commit_sends_once(self, add_event):
        with self.captureOnCommitCallbacks(execute=True):
            utils.bk_audit_add_event_on_commit(
                username="admin", action_id="task_edit", resource_id="task", instance=mock.Mock(id=1)
            )

        add_event.assert_called_once()

    @override_settings(ENABLE_BK_AUDIT=True)
    @mock.patch("gcloud.contrib.audit.utils.bk_audit_add_event")
    def test_rollback_does_not_send(self, add_event):
        with self.captureOnCommitCallbacks(execute=True):
            try:
                with transaction.atomic():
                    utils.bk_audit_add_event_on_commit(
                        username="admin", action_id="task_edit", resource_id="task", instance=mock.Mock(id=1)
                    )
                    raise RuntimeError("rollback")
            except RuntimeError:
                pass

        add_event.assert_not_called()
