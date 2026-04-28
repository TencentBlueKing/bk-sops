# -*- coding: utf-8 -*-

from django.test import SimpleTestCase

from gcloud.contrib.admin.diagnostics.alerts import build_task_alert_payload, emit_task_alert


class DiagnosticCaseStub(object):
    root_pipeline_id = "root-1"
    node_id = "node-1"
    stuck_type = "callback_lock_conflict"
    severity = "critical"
    evidence = {"callback_data_count": 2}
    recommended_actions = ["replay_callback_data"]
    message = "callback conflict"


class TaskDiagnosticAlertsTestCase(SimpleTestCase):
    def test_build_task_alert_payload(self):
        payload = build_task_alert_payload(DiagnosticCaseStub(), {"task_id": 1, "project_id": 2})

        self.assertEqual(payload["task_id"], 1)
        self.assertEqual(payload["project_id"], 2)
        self.assertEqual(payload["root_pipeline_id"], "root-1")
        self.assertEqual(payload["stuck_type"], "callback_lock_conflict")
        self.assertEqual(payload["recommended_actions"], ["replay_callback_data"])

    def test_emit_task_alert_logs_payload(self):
        with self.assertLogs("root", level="WARNING") as logs:
            payload = emit_task_alert(DiagnosticCaseStub(), {"task_id": 1, "project_id": 2})

        self.assertEqual(payload["task_id"], 1)
        self.assertIn("[bk_sops_task_diagnostic_alert]", logs.output[0])
