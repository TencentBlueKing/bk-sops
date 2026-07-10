from unittest.mock import Mock, patch

from django.test import TestCase
from requests import HTTPError, RequestException

from gcloud.utils import crypto


def _make_response(status_code):
    response = Mock(status_code=status_code)
    if status_code >= 400:
        response.raise_for_status = Mock(side_effect=HTTPError("status={}".format(status_code), response=response))
    else:
        response.raise_for_status = Mock(return_value=None)
    return response


class PluginGatewayCallbackServiceTestCase(TestCase):
    def setUp(self):
        from gcloud.plugin_gateway.models import PluginGatewayRun

        self.run_model = PluginGatewayRun

    def _create_run(self, **overrides):
        from gcloud.plugin_gateway.models import PluginGatewayRun

        defaults = {
            "plugin_id": "plugin_job_execute",
            "plugin_version": "1.2.0",
            "source_key": "bkflow",
            "client_request_id": "task_1_node_1_attempt_1",
            "open_plugin_run_id": "run-001",
            "callback_url": "https://bkflow.example.com/callback",
            "callback_token": crypto.encrypt("token-001"),
            "run_status": PluginGatewayRun.Status.WAITING_CALLBACK,
            "caller_app_code": "app_code",
            "trigger_payload": {"project_id": 2001},
        }
        defaults.update(overrides)
        return self.run_model.objects.create(**defaults)

    @patch("gcloud.plugin_gateway.services.callbacks.time.sleep")
    @patch("gcloud.plugin_gateway.services.callbacks.requests.post", side_effect=RequestException("timeout"))
    def test_callback_run_handles_request_exception(self, mock_post, mock_sleep):
        from gcloud.plugin_gateway.models import PluginGatewayRun
        from gcloud.plugin_gateway.services.callbacks import PluginGatewayCallbackService

        run = self._create_run()

        result = PluginGatewayCallbackService.callback_run(
            open_plugin_run_id=run.open_plugin_run_id,
            run_status=PluginGatewayRun.Status.SUCCEEDED,
            outputs={"result": "ok"},
        )

        run.refresh_from_db()
        self.assertFalse(result)
        self.assertEqual(run.run_status, PluginGatewayRun.Status.SUCCEEDED)
        self.assertIsNone(run.callback_delivered_at)
        self.assertEqual(mock_post.call_count, PluginGatewayCallbackService.MAX_CALLBACK_RETRIES)
        self.assertEqual(mock_sleep.call_count, PluginGatewayCallbackService.MAX_CALLBACK_RETRIES - 1)

    @patch("gcloud.plugin_gateway.services.callbacks.time.sleep")
    @patch(
        "gcloud.plugin_gateway.services.callbacks.requests.post",
        side_effect=[RequestException("timeout"), _make_response(200)],
    )
    def test_callback_run_retries_until_success(self, mock_post, mock_sleep):
        from gcloud.plugin_gateway.models import PluginGatewayRun
        from gcloud.plugin_gateway.services.callbacks import PluginGatewayCallbackService

        run = self._create_run()

        result = PluginGatewayCallbackService.callback_run(
            open_plugin_run_id=run.open_plugin_run_id,
            run_status=PluginGatewayRun.Status.SUCCEEDED,
            outputs={"result": "ok"},
        )

        run.refresh_from_db()
        self.assertTrue(result)
        self.assertIsNotNone(run.callback_delivered_at)
        self.assertEqual(mock_post.call_count, 2)
        mock_sleep.assert_called_once_with(PluginGatewayCallbackService.RETRY_BACKOFF_SECONDS)

    @patch("gcloud.plugin_gateway.services.callbacks.time.sleep")
    @patch(
        "gcloud.plugin_gateway.services.callbacks.requests.post",
        return_value=_make_response(500),
    )
    def test_callback_run_treats_5xx_as_failure_and_retries(self, mock_post, mock_sleep):
        from gcloud.plugin_gateway.models import PluginGatewayRun
        from gcloud.plugin_gateway.services.callbacks import PluginGatewayCallbackService

        run = self._create_run()

        result = PluginGatewayCallbackService.callback_run(
            open_plugin_run_id=run.open_plugin_run_id,
            run_status=PluginGatewayRun.Status.SUCCEEDED,
            outputs={"result": "ok"},
        )

        run.refresh_from_db()
        self.assertFalse(result)
        self.assertIsNone(run.callback_delivered_at)
        self.assertEqual(mock_post.call_count, PluginGatewayCallbackService.MAX_CALLBACK_RETRIES)

    @patch("gcloud.plugin_gateway.services.callbacks.requests.post", return_value=_make_response(200))
    def test_callback_run_compensation_retry_uses_stored_outputs(self, mock_post):
        from gcloud.plugin_gateway.models import PluginGatewayRun
        from gcloud.plugin_gateway.services.callbacks import PluginGatewayCallbackService

        run = self._create_run(
            run_status=PluginGatewayRun.Status.SUCCEEDED,
            outputs={"result": "stored"},
            error_message="",
        )

        result = PluginGatewayCallbackService.callback_run(open_plugin_run_id=run.open_plugin_run_id)

        run.refresh_from_db()
        self.assertTrue(result)
        self.assertIsNotNone(run.callback_delivered_at)
        posted_payload = mock_post.call_args[1]["json"]
        self.assertEqual(posted_payload["outputs"], {"result": "stored"})
        self.assertEqual(posted_payload["status"], PluginGatewayRun.Status.SUCCEEDED)

    @patch("gcloud.plugin_gateway.services.callbacks.requests.post", return_value=_make_response(200))
    def test_callback_run_skips_when_already_delivered(self, mock_post):
        from django.utils import timezone

        from gcloud.plugin_gateway.models import PluginGatewayRun
        from gcloud.plugin_gateway.services.callbacks import PluginGatewayCallbackService

        run = self._create_run(
            run_status=PluginGatewayRun.Status.SUCCEEDED,
            callback_delivered_at=timezone.now(),
        )

        result = PluginGatewayCallbackService.callback_run(
            open_plugin_run_id=run.open_plugin_run_id,
            run_status=PluginGatewayRun.Status.SUCCEEDED,
            outputs={"result": "ok"},
        )

        self.assertFalse(result)
        mock_post.assert_not_called()

    @patch("gcloud.plugin_gateway.services.callbacks.requests.post", return_value=_make_response(200))
    def test_callback_run_rejects_state_override_in_terminal(self, mock_post):
        from gcloud.plugin_gateway.models import PluginGatewayRun
        from gcloud.plugin_gateway.services.callbacks import PluginGatewayCallbackService

        run = self._create_run(run_status=PluginGatewayRun.Status.SUCCEEDED)

        result = PluginGatewayCallbackService.callback_run(
            open_plugin_run_id=run.open_plugin_run_id,
            run_status=PluginGatewayRun.Status.FAILED,
            error_message="should be ignored",
        )

        run.refresh_from_db()
        self.assertFalse(result)
        self.assertEqual(run.run_status, PluginGatewayRun.Status.SUCCEEDED)
        mock_post.assert_not_called()

    def test_truncate_outputs_keeps_summary(self):
        from gcloud.plugin_gateway.services.callbacks import PluginGatewayCallbackService

        oversized_outputs = {"payload": "x" * (PluginGatewayCallbackService.MAX_OUTPUT_BYTES + 1)}

        truncated_outputs, truncated, truncated_fields = PluginGatewayCallbackService._truncate_outputs(
            oversized_outputs
        )

        self.assertTrue(truncated)
        self.assertEqual(truncated_fields, ["outputs"])
        self.assertTrue(truncated_outputs["_truncated"])
        self.assertIn("_summary", truncated_outputs)
