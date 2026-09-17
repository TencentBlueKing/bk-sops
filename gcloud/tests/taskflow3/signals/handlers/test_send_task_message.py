from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase

from gcloud.constants import TaskCreateMethod, WebhookEventType
from gcloud.shortcuts.message import TASK_FINISHED
from gcloud.taskflow3.signals import handlers


class AiNotificationAvailabilityTestCase(SimpleTestCase):
    def setUp(self):
        self.enterContext(
            patch.multiple(handlers.env, AI_SOPS_AGENT_URL="https://agent.example.test/prod", ENABLE_AI_NOTIFICATION=1)
        )
        self.task = MagicMock(id=1, template_id=2, create_method=TaskCreateMethod.API.value)
        self.task.pipeline_instance.start_time = datetime(2026, 1, 1, tzinfo=timezone.utc)
        self.task.pipeline_instance.finish_time = None
        self.task.get_task_detail.return_value = {"outputs": []}
        self.task.get_ai_notify_type.return_value = {"success": ["weixin"], "fail": []}
        self.task.get_ai_notify_group.return_value = [{"chat_id": "test-chat"}]
        self.enterContext(patch.object(handlers.TaskFlowInstance.objects, "get", return_value=self.task))
        dispatcher = self.enterContext(patch.object(handlers, "TaskCommandDispatcher"))
        dispatcher.return_value.render_current_constants.return_value = {"result": True, "data": []}
        self.personal_notify = self.enterContext(patch.object(handlers.ai_analysis_notify, "apply_async"))
        self.group_notify = self.enterContext(patch.object(handlers.ai_analysis_notify_group_chat, "apply_async"))
        self.webhook = self.enterContext(patch.object(handlers.event_broadcast_signal, "send"))

    def assert_ai_skipped_and_webhook_sent(self):
        handlers.send_task_message("pipeline-id", "node-id", TASK_FINISHED)

        self.task.get_ai_notify_type.assert_not_called()
        self.task.get_ai_notify_group.assert_not_called()
        self.personal_notify.assert_not_called()
        self.group_notify.assert_not_called()
        self.webhook.assert_called_once()
        self.assertEqual(self.webhook.call_args.kwargs["sender"], WebhookEventType.TASK_FINISHED.value)

    def test_missing_agent_skips_ai_notifications_without_interrupting_webhook(self):
        for host in ("", None, " \t "):
            with self.subTest(host=host), patch.object(handlers.env, "AI_SOPS_AGENT_URL", host):
                self.webhook.reset_mock()
                self.assert_ai_skipped_and_webhook_sent()

    @patch.object(handlers.env, "ENABLE_AI_NOTIFICATION", 0)
    def test_disabled_notification_switch_skips_ai(self):
        self.assert_ai_skipped_and_webhook_sent()

    def test_periodic_tasks_still_skip_ai(self):
        self.task.create_method = TaskCreateMethod.PERIODIC.value
        self.assert_ai_skipped_and_webhook_sent()

    def test_configured_agent_dispatches_personal_and_group_notifications(self):
        handlers.send_task_message("pipeline-id", "node-id", TASK_FINISHED)

        self.personal_notify.assert_called_once()
        self.group_notify.assert_called_once()
        self.assertEqual(self.personal_notify.call_args.kwargs["queue"], "ai_notify")
        self.assertEqual(self.group_notify.call_args.kwargs["queue"], "ai_notify")
        self.webhook.assert_called_once()
