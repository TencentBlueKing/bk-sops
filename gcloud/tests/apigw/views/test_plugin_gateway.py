"""Tests for plugin gateway APIGW endpoints."""

from unittest.mock import Mock, patch

import ujson as json

from gcloud import err_code
from gcloud.tests.apigw.views.utils import TEST_APP_CODE, TEST_USERNAME, APITest


class PluginGatewayAPITest(APITest):
    HEX_RUN_ID = "4f3c2b1a0d9e8f7766554433221100aa"

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
            is_enabled=True,
        )

    def _valid_plugin_reference(self, plugin_id="plugin_job_execute", version="1.2.0"):
        return {
            "id": plugin_id,
            "name": "JOB 执行作业",
            "plugin_source": "third_party",
            "plugin_code": plugin_id,
            "versions": [version],
            "default_version": version,
            "latest_version": version,
        }

    def _valid_create_body(self):
        return {
            "source_key": "bkflow",
            "plugin_id": "plugin_job_execute",
            "plugin_version": "1.2.0",
            "client_request_id": "task_1_node_1_attempt_1",
            "callback_url": "https://bkflow.example.com/callback",
            "callback_token": "token-001",
            "inputs": {"biz_id": 2},
        }

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
                            "http://testserver/apigw/plugin-gateway/plugins/" "bk_plugin_demo/?version={version}"
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

    def test_get_plugin_categories_returns_uniform_api_category_array(self):
        categories = [{"id": "builtin", "name": "标准运维内置插件"}]
        with patch(
            "gcloud.apigw.views.plugin_gateway.PluginGatewayCatalogService.get_categories",
            return_value=categories,
        ) as mock_get_categories:
            response = self.client.get(
                path="/apigw/plugin-gateway/categories/",
                data={"plugin_source": "builtin"},
            )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data["result"], msg=data)
        self.assertEqual(data["data"], categories)
        mock_get_categories.assert_called_once_with(plugin_source="builtin")

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

    @patch("gcloud.plugin_gateway.services.execution.dispatch_plugin_gateway_run.apply_async")
    @patch("gcloud.plugin_gateway.services.execution.PluginGatewayCatalogService.get_plugin_reference")
    def test_create_run_does_not_require_per_plugin_source_config(self, mock_get_plugin_reference, mock_dispatch):
        mock_get_plugin_reference.return_value = self._valid_plugin_reference()
        self.source_model.objects.create(
            source_key="strict-source",
            display_name="Strict Source",
            default_project_id=2001,
            callback_domain_allow_list=["bkflow.example.com"],
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
        self.assertTrue(data["result"], msg=data)
        self.assertEqual(data["code"], err_code.SUCCESS.code)
        mock_dispatch.assert_called_once()

    @patch("gcloud.apigw.views.plugin_gateway.PluginGatewayCatalogService.get_plugin_detail")
    def test_get_plugin_detail_rejects_unknown_version(self, mock_get_plugin_detail):
        from gcloud.plugin_gateway.exceptions import PluginGatewayVersionNotFoundError

        mock_get_plugin_detail.side_effect = PluginGatewayVersionNotFoundError(
            "plugin(plugin_job_execute) version(0.0.0) is not available"
        )
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

    @patch("gcloud.plugin_gateway.services.execution.dispatch_plugin_gateway_run.apply_async")
    @patch("gcloud.plugin_gateway.services.execution.PluginGatewayCatalogService.get_plugin_reference")
    def test_create_run_rejects_idempotent_conflict(self, mock_get_plugin_reference, mock_dispatch):
        mock_get_plugin_reference.return_value = self._valid_plugin_reference()
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
            open_plugin_run_id=self.HEX_RUN_ID,
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
        self.assertEqual(data["data"]["open_plugin_run_id"], self.HEX_RUN_ID)

    @patch("gcloud.apigw.views.plugin_gateway.PluginGatewayExecutionService.create_run")
    def test_create_run_context_resolve_error_returns_400(self, mock_create_run):
        from gcloud.plugin_gateway.exceptions import PluginGatewayContextResolveError

        mock_create_run.side_effect = PluginGatewayContextResolveError("cannot resolve project")

        response = self.client.post(
            path="/apigw/plugin-gateway/runs/",
            data=json.dumps(self._valid_create_body()),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertFalse(data["result"], msg=data)
        self.assertEqual(data["code"], err_code.REQUEST_PARAM_INVALID.code)

    @patch("gcloud.apigw.views.plugin_gateway.PluginGatewayExecutionService.create_run")
    def test_create_run_plugin_not_enabled_returns_400(self, mock_create_run):
        from gcloud.plugin_gateway.exceptions import PluginGatewayPluginNotEnabledError

        mock_create_run.side_effect = PluginGatewayPluginNotEnabledError("plugin is not enabled")

        response = self.client.post(
            path="/apigw/plugin-gateway/runs/",
            data=json.dumps(self._valid_create_body()),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertFalse(data["result"], msg=data)
        self.assertEqual(data["code"], err_code.REQUEST_PARAM_INVALID.code)

    @patch("gcloud.apigw.views.plugin_gateway.PluginGatewayExecutionService.create_run")
    def test_create_run_falls_back_to_apigw_username_for_operator(self, mock_create_run):
        run = self.run_model(
            open_plugin_run_id=self.HEX_RUN_ID,
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
            HTTP_BK_USERNAME=TEST_USERNAME,
        )

        self.assertEqual(response.status_code, 200)
        _, kwargs = mock_create_run.call_args
        self.assertEqual(kwargs["payload"]["operator"], TEST_USERNAME)

    @patch("gcloud.apigw.views.plugin_gateway.PluginGatewayExecutionService.create_run")
    def test_create_run_keeps_explicit_operator_over_apigw_username(self, mock_create_run):
        run = self.run_model(
            open_plugin_run_id=self.HEX_RUN_ID,
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
            "operator": "bkflow-user",
        }

        response = self.client.post(
            path="/apigw/plugin-gateway/runs/",
            data=json.dumps(payload),
            content_type="application/json",
            HTTP_BK_USERNAME=TEST_USERNAME,
        )

        self.assertEqual(response.status_code, 200)
        _, kwargs = mock_create_run.call_args
        self.assertEqual(kwargs["payload"]["operator"], "bkflow-user")

    def test_caller_app_code_requires_apigw_app(self):
        from gcloud.apigw.views.plugin_gateway import _caller_app_code

        request = Mock()
        request.app = None

        with self.assertRaisesRegex(PermissionError, "authorized via apigw"):
            _caller_app_code(request)

    @patch("gcloud.apigw.views.plugin_gateway.PluginGatewayExecutionService.create_run")
    @patch(
        "gcloud.apigw.views.plugin_gateway._caller_app_code",
        side_effect=PermissionError("request app code is missing"),
    )
    def test_create_run_returns_forbidden_when_apigw_app_code_missing(self, _, mock_create_run):
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
        self.assertFalse(data["result"], msg=data)
        self.assertEqual(data["code"], err_code.REQUEST_FORBIDDEN_INVALID.code)
        mock_create_run.assert_not_called()

    @patch("gcloud.plugin_gateway.services.execution.PluginGatewayCallbackService.callback_run")
    def test_cancel_run_accepts_path_without_trailing_slash(self, mock_callback_run):
        run = self.run_model.objects.create(
            source_key="bkflow",
            plugin_id="bk_plugin_demo",
            plugin_version="1.1.0",
            client_request_id="task_1_node_1_attempt_1",
            open_plugin_run_id=self.HEX_RUN_ID,
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
        mock_callback_run.assert_called_once()

    @patch("gcloud.apigw.views.plugin_gateway.callback_plugin_gateway_run.apply_async")
    def test_internal_callback_enqueues_schedule(self, mock_apply_async):
        run = self.run_model.objects.create(
            source_key="bkflow",
            plugin_id="bk_plugin_demo",
            plugin_version="1.1.0",
            client_request_id="task_1_node_1_attempt_1",
            open_plugin_run_id=self.HEX_RUN_ID,
            callback_url="https://bkflow.example.com/callback",
            callback_token="token-001",
            run_status="WAITING_CALLBACK",
            caller_app_code=TEST_APP_CODE,
            trigger_payload={"project_id": 2001},
        )

        response = self.client.post(
            path="/apigw/plugin-gateway/runs/{}/internal-callback/".format(run.open_plugin_run_id),
            data=json.dumps({"callback_data": {"result": "ok"}}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data["result"], msg=data)
        self.assertEqual(data["data"]["open_plugin_run_id"], run.open_plugin_run_id)
        mock_apply_async.assert_called_once_with(
            kwargs={
                "open_plugin_run_id": run.open_plugin_run_id,
                "callback_data": {"result": "ok"},
            },
            queue="open_plugin_callback",
        )
