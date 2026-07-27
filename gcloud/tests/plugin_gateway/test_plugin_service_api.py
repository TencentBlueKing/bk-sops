from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings

from gcloud.plugin_gateway.constants import PLUGIN_SOURCE_THIRD_PARTY
from gcloud.plugin_gateway.exceptions import PluginGatewaySourceUnavailableError

ALLOWED_ORIGIN = "https://stag-dot-bkflow-eng-svc.bkapps-sz.woa.com"


@override_settings(
    PLUGIN_GATEWAY_FORM_CORS_ALLOW=True,
    PLUGIN_GATEWAY_FORM_CORS_ALLOWED_ORIGINS={ALLOWED_ORIGIN},
)
class PluginServiceDataApiTestCase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="form-user")
        self.client.force_login(self.user)
        self.login_patcher = patch(
            "blueapps.account.middlewares.LoginRequiredMiddleware.authenticate",
            return_value=self.user,
        )
        self.login_patcher.start()
        self.addCleanup(self.login_patcher.stop)

    @patch("plugin_service.api.PluginServiceApiClient")
    @patch("plugin_service.api.PluginGatewayCatalogService.get_plugin_reference")
    def test_cross_origin_data_api_requires_visible_plugin(self, get_reference, client_cls):
        get_reference.return_value = None
        response = self.client.get(
            "/plugin_service/data_api/blocked/demo/",
            HTTP_ORIGIN=ALLOWED_ORIGIN,
        )

        self.assertEqual(response.status_code, 403)
        client_cls.assert_not_called()

    @patch("plugin_service.api.PluginServiceApiClient")
    @patch("plugin_service.api.PluginGatewayCatalogService.get_plugin_reference")
    def test_cross_origin_data_api_rejects_visible_builtin_plugin(self, get_reference, client_cls):
        get_reference.return_value = {
            "id": "builtin_demo",
            "plugin_code": "demo",
            "plugin_source": "builtin",
        }
        response = self.client.get(
            "/plugin_service/data_api/demo/options/",
            HTTP_ORIGIN=ALLOWED_ORIGIN,
        )

        self.assertEqual(response.status_code, 403)
        client_cls.assert_not_called()

    @patch("plugin_service.api.PluginGatewayCatalogService.get_plugin_reference")
    @patch("plugin_service.api.PluginServiceApiClient")
    def test_data_api_without_origin_keeps_legacy_behavior(self, client_cls, get_reference):
        client_cls.return_value.dispatch_plugin_api_request.return_value = {
            "result": True,
            "data": {"ok": True},
        }

        response = self.client.get("/plugin_service/data_api/demo/options/")

        self.assertEqual(response.status_code, 200)
        get_reference.assert_not_called()
        client_cls.assert_called_once_with("demo")

    @patch("plugin_service.api.PluginGatewayCatalogService.get_plugin_reference")
    @patch("plugin_service.api.PluginServiceApiClient")
    def test_data_api_with_exact_same_origin_keeps_legacy_behavior(self, client_cls, get_reference):
        client_cls.return_value.dispatch_plugin_api_request.return_value = {
            "result": True,
            "data": {"ok": True},
        }

        response = self.client.get(
            "/plugin_service/data_api/demo/options/",
            HTTP_ORIGIN="http://testserver",
        )

        self.assertEqual(response.status_code, 200)
        get_reference.assert_not_called()
        client_cls.assert_called_once_with("demo")

    @patch("plugin_service.api._decrypt_request_data")
    @patch("plugin_service.api.PluginServiceApiClient")
    def test_data_api_rejects_untrusted_null_and_malformed_origins_before_sensitive_work(
        self, client_cls, decrypt_request_data
    ):
        decrypt_request_data.return_value = ({}, {})
        client_cls.return_value.dispatch_plugin_api_request.return_value = {
            "result": True,
            "data": {"ok": True},
        }
        origins = (
            "https://evil.example",
            "null",
            "https://stag-dot-bkflow-eng-svc.bkapps-sz.woa.com/path",
        )

        for origin in origins:
            with self.subTest(origin=origin):
                response = self.client.get(
                    "/plugin_service/data_api/demo/options/",
                    HTTP_ORIGIN=origin,
                    HTTP_COOKIE="bk_token=must-not-forward",
                )
                self.assertEqual(response.status_code, 403)

        client_cls.assert_not_called()
        decrypt_request_data.assert_not_called()

    @patch("plugin_service.api.PluginServiceApiClient")
    @patch("plugin_service.api.PluginGatewayCatalogService.get_plugin_reference")
    def test_cross_origin_data_api_maps_source_failure_to_503_before_client(self, get_reference, client_cls):
        get_reference.side_effect = PluginGatewaySourceUnavailableError("source timed out")

        response = self.client.get(
            "/plugin_service/data_api/demo/options/",
            HTTP_ORIGIN=ALLOWED_ORIGIN,
        )

        self.assertEqual(response.status_code, 503)
        self.assertEqual(
            response.json(),
            {
                "result": False,
                "data": None,
                "message": "plugin source is unavailable",
            },
        )
        client_cls.assert_not_called()

    @patch("plugin_service.api.PluginGatewayCatalogService.get_plugin_reference")
    @patch("plugin_service.api.PluginServiceApiClient")
    def test_visible_cross_origin_data_api_forwards_request_username(self, client_cls, get_reference):
        get_reference.return_value = {
            "id": "demo",
            "plugin_code": "demo",
            "plugin_source": PLUGIN_SOURCE_THIRD_PARTY,
        }
        client_cls.return_value.dispatch_plugin_api_request.return_value = {
            "result": True,
            "data": {"ok": True},
        }

        response = self.client.get(
            "/plugin_service/data_api/demo/options/",
            HTTP_ORIGIN=ALLOWED_ORIGIN,
        )

        self.assertEqual(response.status_code, 200)
        request_params = client_cls.return_value.dispatch_plugin_api_request.call_args[0][0]
        self.assertEqual(request_params["username"], "form-user")
