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
        self.assertEqual(PluginGatewayRun.objects.filter(client_request_id=self.payload["client_request_id"]).count(), 2)

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
