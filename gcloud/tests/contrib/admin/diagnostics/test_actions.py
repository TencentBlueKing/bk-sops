# -*- coding: utf-8 -*-

import mock
from collections import namedtuple

from django.test import SimpleTestCase

from gcloud.contrib.admin.diagnostics.actions import run_task_action


OperationResult = namedtuple("OperationResult", ["result", "message", "data", "blockers"])


class TaskDiagnosticActionsTestCase(SimpleTestCase):
    def test_unknown_action_is_blocked(self):
        result = run_task_action(task_id=1, node_id="node-1", action="patch_ack", operator="admin", mode="dry_run")

        self.assertFalse(result["result"])
        self.assertIn("unsupported action", result["blockers"])

    def test_missing_required_argument_is_blocked(self):
        result = run_task_action(
            task_id=1,
            node_id="node-1",
            action="replay_callback_data",
            operator="admin",
            mode="dry_run",
        )

        self.assertFalse(result["result"])
        self.assertIn("callback_data_id is required", result["blockers"])

    def test_supported_action_returns_operation_result_dict(self):
        operation = mock.MagicMock(
            return_value=OperationResult(result=True, message="", data={"ready": True}, blockers=[])
        )

        with mock.patch("gcloud.contrib.admin.diagnostics.actions._load_operation", return_value=operation):
            result = run_task_action(
                task_id=1,
                node_id="node-1",
                action="inspect_node_runtime_readiness",
                operator="admin",
                mode="dry_run",
                root_pipeline_id="root-1",
            )

        operation.assert_called_once_with("root-1", "node-1", operator="admin", mode="dry_run")
        self.assertEqual(result, {"result": True, "message": "", "data": {"ready": True}, "blockers": []})
