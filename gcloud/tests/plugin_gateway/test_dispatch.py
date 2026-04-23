from unittest.mock import Mock, patch

from django.test import TestCase

from gcloud.plugin_gateway.models import PluginGatewayRun
from gcloud.plugin_gateway.tasks import dispatch_plugin_gateway_run
from gcloud.utils import crypto


class PluginGatewayDispatchTaskTestCase(TestCase):
    def _create_run(self, **overrides):
        defaults = {
            "plugin_id": "bk_plugin_demo",
            "plugin_version": "1.1.0",
            "source_key": "bkflow",
            "client_request_id": "task_1_node_1_attempt_1",
            "open_plugin_run_id": "run-001",
            "callback_url": "https://bkflow.example.com/callback",
            "callback_token": crypto.encrypt("token-001"),
            "run_status": PluginGatewayRun.Status.WAITING_CALLBACK,
            "caller_app_code": "bkflow-app",
            "trigger_payload": {"project_id": 2001, "inputs": {"biz_id": 2}},
        }
        defaults.update(overrides)
        return PluginGatewayRun.objects.create(**defaults)

    @patch("gcloud.plugin_gateway.tasks.PluginGatewayCallbackService.callback_run")
    @patch("gcloud.plugin_gateway.tasks.PluginServiceApiClient")
    def test_dispatch_run_callbacks_success_for_sync_plugin(self, mock_client_cls, mock_callback_run):
        run = self._create_run()
        mock_client = Mock()
        mock_client.get_detail.return_value = {
            "result": True,
            "data": {"context_inputs": {"properties": {"project_id": {}, "operator": {}}}},
        }
        mock_client.invoke.return_value = (True, {"state": 4, "outputs": {"job_instance_id": 123}})
        mock_client_cls.return_value = mock_client

        dispatch_plugin_gateway_run(open_plugin_run_id=run.open_plugin_run_id)

        mock_callback_run.assert_called_once_with(
            open_plugin_run_id=run.open_plugin_run_id,
            run_status=PluginGatewayRun.Status.SUCCEEDED,
            outputs={"job_instance_id": 123},
        )

    @patch("gcloud.plugin_gateway.tasks.PluginGatewayCallbackService.callback_run")
    @patch("gcloud.plugin_gateway.tasks.PluginServiceApiClient")
    def test_dispatch_run_fails_fast_for_async_runtime_state(self, mock_client_cls, mock_callback_run):
        run = self._create_run()
        mock_client = Mock()
        mock_client.get_detail.return_value = {
            "result": True,
            "data": {"context_inputs": {"properties": {}}},
        }
        mock_client.invoke.return_value = (True, {"state": 2, "trace_id": "trace-001"})
        mock_client_cls.return_value = mock_client

        dispatch_plugin_gateway_run(open_plugin_run_id=run.open_plugin_run_id)

        _, kwargs = mock_callback_run.call_args
        self.assertEqual(kwargs["open_plugin_run_id"], run.open_plugin_run_id)
        self.assertEqual(kwargs["run_status"], PluginGatewayRun.Status.FAILED)
        self.assertIn("asynchronous state", kwargs["error_message"])

    @patch("gcloud.plugin_gateway.tasks.PluginGatewayCallbackService.callback_run")
    @patch("gcloud.plugin_gateway.tasks.PluginServiceApiClient")
    def test_dispatch_run_prefers_operator_from_trigger_payload(self, mock_client_cls, mock_callback_run):
        run = self._create_run(trigger_payload={"project_id": 2001, "operator": "bkflow-user", "inputs": {"biz_id": 2}})
        mock_client = Mock()
        mock_client.get_detail.return_value = {
            "result": True,
            "data": {"context_inputs": {"properties": {"project_id": {}, "operator": {}, "executor": {}}}},
        }
        mock_client.invoke.return_value = (True, {"state": 4, "outputs": {"job_instance_id": 123}})
        mock_client_cls.return_value = mock_client

        dispatch_plugin_gateway_run(open_plugin_run_id=run.open_plugin_run_id)

        _, invoke_payload = mock_client.invoke.call_args[0]
        self.assertEqual(invoke_payload["context"]["operator"], "bkflow-user")
        self.assertEqual(invoke_payload["context"]["executor"], "bkflow-user")
