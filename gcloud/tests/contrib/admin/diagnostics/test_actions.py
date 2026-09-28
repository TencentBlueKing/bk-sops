# -*- coding: utf-8 -*-

from collections import namedtuple

import mock
from django.test import SimpleTestCase

from gcloud.contrib.admin.diagnostics.actions import run_case_replay, run_task_action

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

    def test_case_replay_delegates_to_engine(self):
        replay = mock.MagicMock(return_value=OperationResult(True, "replay preview", {"case_id": 7}, []))

        with mock.patch("pipeline.contrib.diagnostics.recovery.replay_case", replay):
            result = run_case_replay(7, "admin", mode="apply", confirm_risk=True)

        replay.assert_called_once_with(7, "admin", mode="apply", confirm_risk=True)
        self.assertEqual(result, {"result": True, "message": "replay preview", "data": {"case_id": 7}, "blockers": []})

    def test_case_replay_degrades_on_old_engine(self):
        with mock.patch.dict("sys.modules", {"pipeline.contrib.diagnostics.recovery": None}):
            result = run_case_replay(7, "admin")

        self.assertFalse(result["result"])
        self.assertIn("pipeline diagnostics is unavailable", result["message"])
