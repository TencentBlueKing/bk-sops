"""Tests for plugin gateway APIGW endpoints."""

import ujson as json
from unittest.mock import patch

from gcloud import err_code
from gcloud.tests.apigw.views.utils import TEST_APP_CODE, APITest


class PluginGatewayAPITest(APITest):
    def url(self):
        return "/apigw/plugin-gateway/plugins/"

    def setUp(self):
        super().setUp()
        from gcloud.plugin_gateway.models import PluginGatewayRun, PluginGatewaySourceConfig

        self.run_model = PluginGatewayRun
        self.source_model = PluginGatewaySourceConfig
        self.source_model.objects.create(
            source_key="bkflow",
            display_name="BKFlow",
            default_project_id=2001,
            callback_domain_allow_list=["bkflow.example.com"],
            plugin_allow_list=["plugin_job_execute", "plugin_job_status"],
            is_enabled=True,
        )

    def test_get_plugin_list_under_apigw_prefix(self):
        with patch(
            "gcloud.apigw.views.plugin_gateway.PluginGatewayCatalogService.get_plugin_list"
        ) as mock_get_plugin_list:
            mock_get_plugin_list.return_value = {
                "apis": [
                    {
                        "id": "bk_plugin_demo",
                        "name": "Demo Plugin",
                        "category": "third_party",
                        "meta_url_template": (
                            "http://testserver/apigw/plugin-gateway/plugins/"
                            "bk_plugin_demo/?version={version}"
                        ),
                    }
                ]
            }
            response = self.client.get(path="/apigw/plugin-gateway/plugins/")

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)

        self.assertTrue(data["result"], msg=data)
        self.assertTrue(data["data"]["apis"], msg=data)
        self.assertIn("/apigw/plugin-gateway/plugins/", data["data"]["apis"][0]["meta_url_template"])
        self.assertEqual(data["data"]["apis"][0]["category"], "third_party")

    def test_create_run_rejects_unknown_source_with_4xx_payload(self):
        payload = {
            "source_key": "missing-source",
            "plugin_id": "plugin_job_execute",
            "plugin_version": "1.2.0",
            "client_request_id": "task_1_node_1_attempt_1",
            "callback_url": "https://bkflow.example.com/callback",
            "callback_token": "token-001",
            "inputs": {"biz_id": 2},
        }

        response = self.client.post(
            path="/apigw/plugin-gateway/runs/",
            data=json.dumps(payload),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertFalse(data["result"], msg=data)
        self.assertEqual(data["code"], err_code.CONTENT_NOT_EXIST.code)
        self.assertEqual(data["error_type"], "source_unreachable")

    def test_create_run_rejects_malformed_callback_url(self):
        payload = {
            "source_key": "bkflow",
            "plugin_id": "plugin_job_execute",
            "plugin_version": "1.2.0",
            "client_request_id": "task_1_node_1_attempt_1",
            "callback_url": "bkflow.example.com/callback",
            "callback_token": "token-001",
            "inputs": {"biz_id": 2},
        }

        response = self.client.post(
            path="/apigw/plugin-gateway/runs/",
            data=json.dumps(payload),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertFalse(data["result"], msg=data)
        self.assertEqual(data["code"], err_code.REQUEST_PARAM_INVALID.code)

    def test_create_run_rejects_empty_allow_lists(self):
        self.source_model.objects.create(
            source_key="strict-source",
            display_name="Strict Source",
            default_project_id=2001,
            callback_domain_allow_list=[],
            plugin_allow_list=[],
            is_enabled=True,
        )
        payload = {
            "source_key": "strict-source",
            "plugin_id": "plugin_job_execute",
            "plugin_version": "1.2.0",
            "client_request_id": "task_1_node_1_attempt_1",
            "callback_url": "https://bkflow.example.com/callback",
            "callback_token": "token-001",
            "inputs": {"biz_id": 2},
        }

        response = self.client.post(
            path="/apigw/plugin-gateway/runs/",
            data=json.dumps(payload),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertFalse(data["result"], msg=data)
        self.assertEqual(data["code"], err_code.REQUEST_PARAM_INVALID.code)

    def test_get_plugin_detail_rejects_unknown_version(self):
        response = self.client.get(path="/apigw/plugin-gateway/plugins/plugin_job_execute/?version=0.0.0")

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertFalse(data["result"], msg=data)
        self.assertEqual(data["code"], err_code.REQUEST_PARAM_INVALID.code)

    def test_get_plugin_detail_returns_not_found_for_unknown_plugin(self):
        response = self.client.get(path="/apigw/plugin-gateway/plugins/does_not_exist/")

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertFalse(data["result"], msg=data)
        self.assertEqual(data["code"], err_code.CONTENT_NOT_EXIST.code)
        self.assertEqual(data["error_type"], "plugin_removed")

    def test_create_run_rejects_idempotent_conflict(self):
        payload = {
            "source_key": "bkflow",
            "plugin_id": "plugin_job_execute",
            "plugin_version": "1.2.0",
            "client_request_id": "task_1_node_1_attempt_1",
            "callback_url": "https://bkflow.example.com/callback",
            "callback_token": "token-001",
            "inputs": {"biz_id": 2},
        }

        first = self.client.post(
            path="/apigw/plugin-gateway/runs/",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(first.status_code, 200)

        conflict_payload = dict(payload)
        conflict_payload["callback_url"] = "https://bkflow.example.com/other-callback"

        second = self.client.post(
            path="/apigw/plugin-gateway/runs/",
            data=json.dumps(conflict_payload),
            content_type="application/json",
        )

        self.assertEqual(second.status_code, 200)
        data = json.loads(second.content)
        self.assertFalse(data["result"], msg=data)
        self.assertEqual(data["code"], err_code.INVALID_OPERATION.code)
        self.assertEqual(
            self.run_model.objects.filter(
                caller_app_code=TEST_APP_CODE, client_request_id=payload["client_request_id"]
            ).count(),
            1,
        )

    @patch("gcloud.apigw.views.plugin_gateway.PluginGatewayExecutionService.create_run")
    def test_create_run_schedules_dispatch_via_execution_service(self, mock_create_run):
        run = self.run_model(
            open_plugin_run_id="run-001",
            run_status="WAITING_CALLBACK",
            plugin_id="bk_plugin_demo",
            plugin_version="1.1.0",
        )
        mock_create_run.return_value = (run, True)
        payload = {
            "source_key": "bkflow",
            "plugin_id": "bk_plugin_demo",
            "plugin_version": "1.1.0",
            "client_request_id": "task_1_node_1_attempt_1",
            "callback_url": "https://bkflow.example.com/callback",
            "callback_token": "token-001",
            "inputs": {"biz_id": 2},
        }

        response = self.client.post(
            path="/apigw/plugin-gateway/runs/",
            data=json.dumps(payload),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data["result"], msg=data)
        self.assertEqual(data["data"]["open_plugin_run_id"], "run-001")

    def test_cancel_run_accepts_path_without_trailing_slash(self):
        run = self.run_model.objects.create(
            source_key="bkflow",
            plugin_id="bk_plugin_demo",
            plugin_version="1.1.0",
            client_request_id="task_1_node_1_attempt_1",
            open_plugin_run_id="run-001",
            callback_url="https://bkflow.example.com/callback",
            callback_token="token-001",
            run_status="WAITING_CALLBACK",
            caller_app_code=TEST_APP_CODE,
            trigger_payload={"project_id": 2001},
        )

        response = self.client.post(path="/apigw/plugin-gateway/runs/{}/cancel".format(run.open_plugin_run_id))

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data["result"], msg=data)
        self.assertEqual(data["data"]["status"], "CANCELLED")
