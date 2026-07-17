from datetime import timedelta
from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone

from gcloud.plugin_gateway.exceptions import PluginGatewayContextResolveError
from gcloud.plugin_gateway.models import PluginGatewayRun, PluginGatewaySourceConfig
from gcloud.plugin_gateway.tasks import (
    callback_plugin_gateway_run,
    dispatch_plugin_gateway_run,
    poll_plugin_gateway_run,
)
from gcloud.utils import crypto


class PluginGatewayDispatchTaskTestCase(TestCase):
    def setUp(self):
        PluginGatewaySourceConfig.objects.create(
            source_key="bkflow",
            display_name="BKFlow",
            default_project_id=2001,
            callback_domain_allow_list=["bkflow.example.com"],
            is_enabled=True,
        )

    def _create_run(self, **overrides):
        trigger_payload = {
            "context": {"scope_type": "biz", "scope_value": "2", "operator": "bkflow-user"},
            "inputs": {"biz_id": 2},
            "plugin_source": "third_party",
            "plugin_code": "bk_plugin_demo",
        }
        trigger_payload.update(overrides.pop("trigger_payload", {}))
        defaults = {
            "plugin_id": "bk_plugin_demo",
            "plugin_version": "1.1.0",
            "source_key": "bkflow",
            "client_request_id": "task_1_node_1_attempt_1",
            "open_plugin_run_id": "run-001",
            "callback_url": "https://bkflow.example.com/callback",
            "callback_token": crypto.encrypt("token-001"),
            "run_status": PluginGatewayRun.Status.CREATED,
            "caller_app_code": "bkflow-app",
            "trigger_payload": trigger_payload,
        }
        defaults.update(overrides)
        return PluginGatewayRun.objects.create(**defaults)

    @patch("gcloud.plugin_gateway.tasks.PluginGatewayCallbackService.callback_run")
    @patch("gcloud.plugin_gateway.tasks.PluginGatewayRunner.run_execute")
    @patch("gcloud.plugin_gateway.tasks.PluginGatewayContextService.resolve_run_context")
    def test_dispatch_sync_success_calls_callback(self, mock_resolve_context, mock_run_execute, mock_callback_run):
        mock_resolve_context.return_value = {"operator": "bkflow-user", "project_id": 10, "bk_biz_id": 2}
        mock_run_execute.return_value = {
            "ok": True,
            "need_schedule": False,
            "mode": "sync",
            "outputs": {"job_instance_id": 123},
            "error_message": "",
            "finished": False,
        }
        run = self._create_run()

        dispatch_plugin_gateway_run(open_plugin_run_id=run.open_plugin_run_id)

        mock_resolve_context.assert_called_once()
        mock_run_execute.assert_called_once()
        mock_callback_run.assert_called_once_with(
            open_plugin_run_id=run.open_plugin_run_id,
            run_status=PluginGatewayRun.Status.SUCCEEDED,
            outputs={"job_instance_id": 123},
        )

    @patch("gcloud.plugin_gateway.tasks.PluginGatewayCallbackService.callback_run")
    @patch("gcloud.plugin_gateway.tasks.PluginGatewayRunner.run_execute")
    @patch("gcloud.plugin_gateway.tasks.PluginGatewayContextService.resolve_run_context")
    def test_dispatch_context_resolve_error_callbacks_failed(
        self, mock_resolve_context, mock_run_execute, mock_callback_run
    ):
        mock_resolve_context.side_effect = PluginGatewayContextResolveError("cannot resolve project")
        run = self._create_run()

        dispatch_plugin_gateway_run(open_plugin_run_id=run.open_plugin_run_id)

        mock_run_execute.assert_not_called()
        mock_callback_run.assert_called_once_with(
            open_plugin_run_id=run.open_plugin_run_id,
            run_status=PluginGatewayRun.Status.FAILED,
            error_message="cannot resolve project",
        )

    @patch("gcloud.plugin_gateway.tasks.poll_plugin_gateway_run.apply_async")
    @patch("gcloud.plugin_gateway.tasks.PluginGatewayCallbackService.callback_run")
    @patch("gcloud.plugin_gateway.tasks.PluginGatewayRunner.run_execute")
    @patch("gcloud.plugin_gateway.tasks.PluginGatewayContextService.resolve_run_context")
    def test_dispatch_polling_result_persists_runtime_outputs(
        self, mock_resolve_context, mock_run_execute, mock_callback_run, mock_poll_apply_async
    ):
        mock_resolve_context.return_value = {"operator": "bkflow-user", "project_id": 10, "bk_biz_id": 2}
        mock_run_execute.return_value = {
            "ok": True,
            "need_schedule": True,
            "mode": "poll",
            "outputs": {"trace_id": "trace-001"},
            "error_message": "",
            "finished": False,
        }
        run = self._create_run()

        dispatch_plugin_gateway_run(open_plugin_run_id=run.open_plugin_run_id)

        run.refresh_from_db()
        mock_callback_run.assert_not_called()
        self.assertEqual(run.run_status, PluginGatewayRun.Status.RUNNING)
        self.assertEqual(run.runtime_outputs, {"trace_id": "trace-001"})
        self.assertEqual(run.schedule_times, 0)
        mock_poll_apply_async.assert_called_once_with(
            kwargs={"open_plugin_run_id": run.open_plugin_run_id},
            countdown=10,
            queue="open_plugin_polling",
        )

    @patch("gcloud.plugin_gateway.tasks.PluginGatewayCallbackService.callback_run")
    @patch("gcloud.plugin_gateway.tasks.PluginGatewayRunner.run_schedule")
    @patch("gcloud.plugin_gateway.tasks.PluginGatewayContextService.resolve_run_context")
    def test_poll_finished_calls_success_callback(self, mock_resolve_context, mock_run_schedule, mock_callback_run):
        mock_resolve_context.return_value = {"operator": "bkflow-user", "project_id": 10, "bk_biz_id": 2}
        mock_run_schedule.return_value = {
            "ok": True,
            "need_schedule": False,
            "mode": "poll",
            "outputs": {"result": 1},
            "error_message": "",
            "finished": True,
        }
        run = self._create_run(run_status=PluginGatewayRun.Status.RUNNING, runtime_outputs={"trace_id": "trace-001"})

        poll_plugin_gateway_run(open_plugin_run_id=run.open_plugin_run_id)

        run.refresh_from_db()
        self.assertEqual(run.schedule_times, 1)
        self.assertEqual(run.runtime_outputs, {"result": 1})
        mock_callback_run.assert_called_once_with(
            open_plugin_run_id=run.open_plugin_run_id,
            run_status=PluginGatewayRun.Status.SUCCEEDED,
            outputs={"result": 1},
        )

    @patch("gcloud.plugin_gateway.tasks.poll_plugin_gateway_run.apply_async")
    @patch("gcloud.plugin_gateway.tasks.PluginGatewayCallbackService.callback_run")
    @patch("gcloud.plugin_gateway.tasks.PluginGatewayRunner.run_schedule")
    @patch("gcloud.plugin_gateway.tasks.PluginGatewayContextService.resolve_run_context")
    def test_poll_unfinished_requeues(
        self, mock_resolve_context, mock_run_schedule, mock_callback_run, mock_poll_apply_async
    ):
        mock_resolve_context.return_value = {"operator": "bkflow-user", "project_id": 10, "bk_biz_id": 2}
        mock_run_schedule.return_value = {
            "ok": True,
            "need_schedule": True,
            "mode": "poll",
            "outputs": {"trace_id": "trace-002"},
            "error_message": "",
            "finished": False,
        }
        run = self._create_run(run_status=PluginGatewayRun.Status.RUNNING, runtime_outputs={"trace_id": "trace-001"})

        poll_plugin_gateway_run(open_plugin_run_id=run.open_plugin_run_id)

        run.refresh_from_db()
        mock_callback_run.assert_not_called()
        self.assertEqual(run.schedule_times, 1)
        self.assertEqual(run.runtime_outputs, {"trace_id": "trace-002"})
        mock_poll_apply_async.assert_called_once_with(
            kwargs={"open_plugin_run_id": run.open_plugin_run_id},
            countdown=10,
            queue="open_plugin_polling",
        )

    @patch("gcloud.plugin_gateway.tasks.PluginGatewayCallbackService.callback_run")
    @patch("gcloud.plugin_gateway.tasks.PluginGatewayRunner.run_schedule")
    @patch("gcloud.plugin_gateway.tasks.PluginGatewayContextService.resolve_run_context")
    def test_poll_timeout_callbacks_failed(self, mock_resolve_context, mock_run_schedule, mock_callback_run):
        run = self._create_run(
            run_status=PluginGatewayRun.Status.RUNNING,
            execution_expire_at=timezone.now() - timedelta(seconds=1),
        )

        poll_plugin_gateway_run(open_plugin_run_id=run.open_plugin_run_id)

        mock_resolve_context.assert_not_called()
        mock_run_schedule.assert_not_called()
        mock_callback_run.assert_called_once_with(
            open_plugin_run_id=run.open_plugin_run_id,
            run_status=PluginGatewayRun.Status.FAILED,
            error_message="execution timeout",
        )

    @patch("gcloud.plugin_gateway.tasks.PluginGatewayCallbackService.callback_run")
    @patch("gcloud.plugin_gateway.tasks.PluginGatewayRunner.run_schedule")
    @patch("gcloud.plugin_gateway.tasks.PluginGatewayContextService.resolve_run_context")
    def test_poll_exceed_max_schedule_times_callbacks_failed(
        self, mock_resolve_context, mock_run_schedule, mock_callback_run
    ):
        run = self._create_run(run_status=PluginGatewayRun.Status.RUNNING, schedule_times=1000)

        poll_plugin_gateway_run(open_plugin_run_id=run.open_plugin_run_id)

        mock_resolve_context.assert_not_called()
        mock_run_schedule.assert_not_called()
        mock_callback_run.assert_called_once_with(
            open_plugin_run_id=run.open_plugin_run_id,
            run_status=PluginGatewayRun.Status.FAILED,
            error_message="exceed max schedule times",
        )

    @patch("gcloud.plugin_gateway.tasks.PluginGatewayCallbackService.callback_run")
    @patch("gcloud.plugin_gateway.tasks.PluginGatewayRunner.run_schedule")
    @patch("gcloud.plugin_gateway.tasks.PluginGatewayContextService.resolve_run_context")
    def test_callback_task_finishes(self, mock_resolve_context, mock_run_schedule, mock_callback_run):
        mock_resolve_context.return_value = {"operator": "bkflow-user", "project_id": 10, "bk_biz_id": 2}
        mock_run_schedule.return_value = {
            "ok": True,
            "need_schedule": False,
            "mode": "callback",
            "outputs": {"result": 9},
            "error_message": "",
            "finished": True,
        }
        run = self._create_run(run_status=PluginGatewayRun.Status.WAITING_CALLBACK)

        callback_plugin_gateway_run(open_plugin_run_id=run.open_plugin_run_id, callback_data={"result": "ok"})

        run.refresh_from_db()
        self.assertEqual(run.runtime_outputs, {"result": 9})
        mock_run_schedule.assert_called_once_with(
            run,
            {"operator": "bkflow-user", "project_id": 10, "bk_biz_id": 2},
            callback_data={"result": "ok"},
        )
        mock_callback_run.assert_called_once_with(
            open_plugin_run_id=run.open_plugin_run_id,
            run_status=PluginGatewayRun.Status.SUCCEEDED,
            outputs={"result": 9},
        )
