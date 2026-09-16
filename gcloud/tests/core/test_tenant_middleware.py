from unittest import mock

from django.test import SimpleTestCase, override_settings

from gcloud.core.middlewares import TenantMiddleware


class TenantMiddlewareTest(SimpleTestCase):
    def setUp(self):
        self.middleware = TenantMiddleware(lambda request: None)

    @override_settings(ENABLE_MULTI_TENANT_MODE=True, SECURE_PROXY_SSL_HEADER=("HTTP_X_FORWARDED_PROTO", "https"))
    @mock.patch("gcloud.core.middlewares.set_current_tenant_id")
    @mock.patch("gcloud.core.middlewares.get_bk_token_userinfo")
    def test_recovers_missing_tenant_from_current_bk_token(self, get_userinfo, set_tenant):
        get_userinfo.return_value = {"bk_username": "user-id", "tenant_id": "tenant-a"}
        user = mock.Mock(username="user-id", tenant_id="default", is_authenticated=True)
        request = mock.Mock(user=user, COOKIES={"bk_token": "token"})

        self.middleware.process_request(request)

        self.assertEqual(user.tenant_id, "tenant-a")
        user.save.assert_called_once_with(update_fields=["tenant_id"])
        set_tenant.assert_called_once_with("tenant-a")

    @override_settings(ENABLE_MULTI_TENANT_MODE=True, SECURE_PROXY_SSL_HEADER=("HTTP_X_FORWARDED_PROTO", "https"))
    @mock.patch("gcloud.core.middlewares.set_current_tenant_id")
    @mock.patch("gcloud.core.middlewares.get_bk_token_userinfo")
    def test_does_not_accept_tenant_for_a_different_subject(self, get_userinfo, set_tenant):
        get_userinfo.return_value = {"bk_username": "another-user", "tenant_id": "tenant-a"}
        user = mock.Mock(username="user-id", tenant_id="", is_authenticated=True)
        request = mock.Mock(user=user, COOKIES={"bk_token": "token"})

        self.middleware.process_request(request)

        user.save.assert_not_called()
        set_tenant.assert_called_once_with("")

    @override_settings(ENABLE_MULTI_TENANT_MODE=False, SECURE_PROXY_SSL_HEADER=("HTTP_X_FORWARDED_PROTO", "https"))
    @mock.patch("gcloud.core.middlewares.set_current_tenant_id")
    def test_keeps_legacy_default_for_single_tenant_mode(self, set_tenant):
        user = mock.Mock(tenant_id="", is_authenticated=True)
        request = mock.Mock(user=user)

        self.middleware.process_request(request)

        self.assertEqual(user.tenant_id, "default")
        set_tenant.assert_called_once_with("default")
