import json
from unittest import mock

from django.test import SimpleTestCase, override_settings

from gcloud.utils.token_backend import TenantAwareTokenBackend, get_bk_token_userinfo


@override_settings(
    APP_CODE="bk_sops",
    SECRET_KEY="secret",
    BK_API_URL_TMPL="https://api.example.test/api/{api_name}",
)
class TokenUserinfoTest(SimpleTestCase):
    @mock.patch("gcloud.utils.token_backend.requests.get")
    def test_global_app_uses_system_tenant_without_extra_environment_variable(self, request_get):
        response = request_get.return_value
        response.status_code = 200
        response.json.return_value = {"data": {"bk_username": "admin", "tenant_id": "tenant-a"}}

        with mock.patch.dict("os.environ", {"BKPAAS_APP_TENANT_ID": ""}):
            result = get_bk_token_userinfo("token")

        self.assertEqual(result["tenant_id"], "tenant-a")
        _, kwargs = request_get.call_args
        self.assertEqual(kwargs["headers"]["X-Bk-Tenant-Id"], "system")
        self.assertEqual(
            json.loads(kwargs["headers"]["X-Bkapi-Authorization"]),
            {"bk_app_code": "bk_sops", "bk_app_secret": "secret"},
        )

    @mock.patch("gcloud.utils.token_backend.requests.get")
    def test_single_tenant_app_uses_platform_tenant(self, request_get):
        response = request_get.return_value
        response.status_code = 200
        response.json.return_value = {"data": {"bk_username": "user", "tenant_id": "tenant-a"}}

        with mock.patch.dict("os.environ", {"BKPAAS_APP_TENANT_ID": "tenant-a"}):
            get_bk_token_userinfo("token")

        self.assertEqual(request_get.call_args.kwargs["headers"]["X-Bk-Tenant-Id"], "tenant-a")

    @mock.patch("gcloud.utils.token_backend.requests.get")
    def test_rejected_token_returns_none(self, request_get):
        response = request_get.return_value
        response.status_code = 401
        response.json.return_value = {"code": 1302100, "message": "invalid token", "request_id": "request-id"}

        with mock.patch.dict("os.environ", {"BKPAAS_APP_TENANT_ID": ""}):
            result = get_bk_token_userinfo("token")

        self.assertIsNone(result)

    @mock.patch("gcloud.utils.token_backend.get_user_model")
    @mock.patch("gcloud.utils.token_backend.get_bk_token_userinfo")
    def test_backend_persists_the_user_tenant_returned_by_bk_login(self, get_userinfo, get_user_model):
        get_userinfo.return_value = {
            "bk_username": "user",
            "display_name": "User",
            "tenant_id": "tenant-a",
            "bk_role": "0",
        }
        user = mock.Mock(is_superuser=False, is_staff=False)
        get_user_model.return_value.objects.get_or_create.return_value = (user, True)

        result = TenantAwareTokenBackend().authenticate(bk_token="token")

        self.assertIs(result, user)
        self.assertEqual(user.tenant_id, "tenant-a")
        user.save.assert_called_once_with()

    @mock.patch("gcloud.utils.token_backend.get_user_model")
    @mock.patch("gcloud.utils.token_backend.get_bk_token_userinfo")
    def test_backend_accepts_role_field_for_platform_admin(self, get_userinfo, get_user_model):
        get_userinfo.return_value = {
            "bk_username": "admin",
            "tenant_id": "tenant-a",
            "role": "1",
        }
        user = mock.Mock(is_superuser=False, is_staff=False)
        get_user_model.return_value.objects.get_or_create.return_value = (user, True)

        TenantAwareTokenBackend().authenticate(bk_token="token")

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
