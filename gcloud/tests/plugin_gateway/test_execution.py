from unittest.mock import patch

from django.db import IntegrityError
from django.test import TestCase

from gcloud.plugin_gateway.exceptions import PluginGatewayConflictError
from gcloud.plugin_gateway.models import PluginGatewayRun, PluginGatewaySourceConfig
from gcloud.plugin_gateway.services.execution import PluginGatewayExecutionService
from gcloud.utils import crypto


class PluginGatewayExecutionServiceTestCase(TestCase):
    def setUp(self):
        self.source_config = PluginGatewaySourceConfig.objects.create(
            source_key="bkflow",
            display_name="BKFlow",
            default_project_id=2001,
            callback_domain_allow_list=["bkflow.example.com"],
            plugin_allow_list=["plugin_job_execute", "plugin_job_status"],
            is_enabled=True,
        )
        self.payload = {
            "source_key": "bkflow",
            "plugin_id": "plugin_job_execute",
            "plugin_version": "1.2.0",
            "client_request_id": "task_1_node_1_attempt_1",
            "callback_url": "https://bkflow.example.com/callback",
            "callback_token": "token-001",
            "inputs": {"biz_id": 2},
        }

    def test_create_run_scopes_idempotency_by_caller_app_code(self):
        first_run, first_created = PluginGatewayExecutionService.create_run("bkflow-app", self.payload)
        second_run, second_created = PluginGatewayExecutionService.create_run("job-app", self.payload)

        self.assertTrue(first_created)
        self.assertTrue(second_created)
        self.assertNotEqual(first_run.pk, second_run.pk)
        self.assertEqual(
            PluginGatewayRun.objects.filter(client_request_id=self.payload["client_request_id"]).count(), 2
        )

    def test_create_run_encrypts_callback_token(self):
        run, created = PluginGatewayExecutionService.create_run("bkflow-app", self.payload)

        self.assertTrue(created)
        self.assertNotEqual(run.callback_token, self.payload["callback_token"])
        self.assertEqual(crypto.decrypt(run.callback_token), self.payload["callback_token"])

    def test_create_run_rejects_idempotent_conflict_for_same_app(self):
        PluginGatewayExecutionService.create_run("bkflow-app", self.payload)

        conflict_payload = dict(self.payload)
        conflict_payload["plugin_id"] = "plugin_job_status"

        with self.assertRaises(PluginGatewayConflictError):
            PluginGatewayExecutionService.create_run("bkflow-app", conflict_payload)

    def test_create_run_rejects_idempotent_conflict_on_token_only(self):
        PluginGatewayExecutionService.create_run("bkflow-app", self.payload)

        conflict_payload = dict(self.payload)
        conflict_payload["callback_token"] = "token-different"

        with self.assertRaisesRegex(PluginGatewayConflictError, "callback_token"):
            PluginGatewayExecutionService.create_run("bkflow-app", conflict_payload)

    def test_create_run_handles_integrity_error_as_idempotent(self):
        """并发场景下两条请求同时进入 created=True，其中之一被唯一约束拦截，
        应该被转换为幂等复用而不是 500。"""

        first_run, _ = PluginGatewayExecutionService.create_run("bkflow-app", self.payload)

        def _racy_get_or_create(*args, **kwargs):
            # 模拟另一条请求已抢先写入后本次 get_or_create 命中唯一约束
            raise IntegrityError("duplicate key")

        with patch.object(PluginGatewayRun.objects, "get_or_create", side_effect=_racy_get_or_create):
            run, created = PluginGatewayExecutionService.create_run("bkflow-app", self.payload)

        self.assertFalse(created)
        self.assertEqual(run.pk, first_run.pk)

    def test_create_run_fast_path_does_not_decrypt_token_on_clear_conflict(self):
        """当非 token 字段已经不一致时，不应再为比对 token 付出解密成本。"""

        PluginGatewayExecutionService.create_run("bkflow-app", self.payload)

        conflict_payload = dict(self.payload)
        conflict_payload["plugin_id"] = "plugin_job_status"

        with patch("gcloud.plugin_gateway.services.execution.crypto.decrypt") as mock_decrypt:
            with self.assertRaises(PluginGatewayConflictError):
                PluginGatewayExecutionService.create_run("bkflow-app", conflict_payload)

        mock_decrypt.assert_not_called()

    @patch("gcloud.plugin_gateway.services.execution.dispatch_plugin_gateway_run")
    @patch("gcloud.plugin_gateway.services.execution.PluginGatewayCatalogService.get_plugin_reference")
    def test_create_run_dispatches_async_runtime_once_created(self, mock_get_plugin_reference, mock_dispatch_task):
        mock_get_plugin_reference.return_value = {
            "id": "plugin_job_execute",
            "plugin_code": "plugin_job_execute",
            "plugin_source": "third_party",
            "versions": ["1.2.0"],
        }

        run, created = PluginGatewayExecutionService.create_run("bkflow-app", self.payload)

        self.assertTrue(created)
        mock_dispatch_task.apply_async.assert_called_once_with(kwargs={"open_plugin_run_id": run.open_plugin_run_id})

    @patch("gcloud.plugin_gateway.services.execution.PluginGatewayCallbackService.callback_run")
    def test_cancel_run_updates_status_and_triggers_callback(self, mock_callback_run):
        run = PluginGatewayRun.objects.create(
            source_key="bkflow",
            plugin_id="plugin_job_execute",
            plugin_version="1.2.0",
            client_request_id="task_1_node_1_attempt_1",
            open_plugin_run_id="4f3c2b1a0d9e8f7766554433221100aa",
            callback_url="https://bkflow.example.com/callback",
            callback_token=crypto.encrypt("token-001"),
            run_status=PluginGatewayRun.Status.WAITING_CALLBACK,
            caller_app_code="bkflow-app",
            trigger_payload={"project_id": 2001},
        )

        result = PluginGatewayExecutionService.cancel_run(run.open_plugin_run_id, "bkflow-app")

        run.refresh_from_db()
        self.assertEqual(result.run_status, PluginGatewayRun.Status.CANCELLED)
        self.assertEqual(run.run_status, PluginGatewayRun.Status.CANCELLED)
        self.assertEqual(run.error_message, "run cancelled by caller")
        mock_callback_run.assert_called_once_with(
            open_plugin_run_id=run.open_plugin_run_id,
            run_status=PluginGatewayRun.Status.CANCELLED,
            outputs={},
            error_message="run cancelled by caller",
        )
