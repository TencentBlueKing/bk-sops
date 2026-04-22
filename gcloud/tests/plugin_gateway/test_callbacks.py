from unittest.mock import Mock, patch

from requests import RequestException

from django.test import TestCase

from gcloud.utils import crypto


class PluginGatewayCallbackServiceTestCase(TestCase):
    def setUp(self):
        from gcloud.plugin_gateway.models import PluginGatewayRun

        self.run_model = PluginGatewayRun

    @patch("gcloud.plugin_gateway.services.callbacks.time.sleep")
    @patch("gcloud.plugin_gateway.services.callbacks.requests.post", side_effect=RequestException("timeout"))
    def test_callback_run_handles_request_exception(self, mock_post, mock_sleep):
        from gcloud.plugin_gateway.models import PluginGatewayRun
        from gcloud.plugin_gateway.services.callbacks import PluginGatewayCallbackService

        run = self.run_model.objects.create(
            plugin_id="plugin_job_execute",
            plugin_version="1.2.0",
            source_key="bkflow",
            client_request_id="task_1_node_1_attempt_1",
            open_plugin_run_id="run-001",
            callback_url="https://bkflow.example.com/callback",
            callback_token=crypto.encrypt("token-001"),
            run_status=PluginGatewayRun.Status.WAITING_CALLBACK,
            caller_app_code="app_code",
            trigger_payload={"project_id": 2001},
        )

        result = PluginGatewayCallbackService.callback_run(
            open_plugin_run_id=run.open_plugin_run_id,
            run_status=PluginGatewayRun.Status.SUCCEEDED,
            outputs={"result": "ok"},
        )

        run.refresh_from_db()
        self.assertFalse(result)
        self.assertEqual(run.run_status, PluginGatewayRun.Status.SUCCEEDED)
        self.assertEqual(mock_post.call_count, PluginGatewayCallbackService.MAX_CALLBACK_RETRIES)
        self.assertEqual(mock_sleep.call_count, PluginGatewayCallbackService.MAX_CALLBACK_RETRIES - 1)

    @patch("gcloud.plugin_gateway.services.callbacks.time.sleep")
    @patch(
        "gcloud.plugin_gateway.services.callbacks.requests.post",
        side_effect=[RequestException("timeout"), Mock(status_code=200)],
    )
    def test_callback_run_retries_until_success(self, mock_post, mock_sleep):
        from gcloud.plugin_gateway.models import PluginGatewayRun
        from gcloud.plugin_gateway.services.callbacks import PluginGatewayCallbackService

        run = self.run_model.objects.create(
            plugin_id="plugin_job_execute",
            plugin_version="1.2.0",
            source_key="bkflow",
            client_request_id="task_1_node_1_attempt_1",
            open_plugin_run_id="run-001",
            callback_url="https://bkflow.example.com/callback",
            callback_token=crypto.encrypt("token-001"),
            run_status=PluginGatewayRun.Status.WAITING_CALLBACK,
            caller_app_code="app_code",
            trigger_payload={"project_id": 2001},
        )

        result = PluginGatewayCallbackService.callback_run(
            open_plugin_run_id=run.open_plugin_run_id,
            run_status=PluginGatewayRun.Status.SUCCEEDED,
            outputs={"result": "ok"},
        )

        self.assertTrue(result)
        self.assertEqual(mock_post.call_count, 2)
        mock_sleep.assert_called_once_with(PluginGatewayCallbackService.RETRY_BACKOFF_SECONDS)

    def test_truncate_outputs_keeps_summary(self):
        from gcloud.plugin_gateway.services.callbacks import PluginGatewayCallbackService

        oversized_outputs = {"payload": "x" * (PluginGatewayCallbackService.MAX_OUTPUT_BYTES + 1)}

        truncated_outputs, truncated, truncated_fields = PluginGatewayCallbackService._truncate_outputs(oversized_outputs)

        self.assertTrue(truncated)
        self.assertEqual(truncated_fields, ["outputs"])
        self.assertTrue(truncated_outputs["_truncated"])
        self.assertIn("_summary", truncated_outputs)
