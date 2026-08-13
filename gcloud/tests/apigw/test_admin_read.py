import json
from types import SimpleNamespace
from unittest import mock

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from gcloud import err_code
from gcloud.apigw.decorators import mark_admin_read_request
from gcloud.apigw.utils import api_hash_key


class AdminReadDecoratorTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create(username="po_admin")

    def build_request(self, method="get", admin_header="true", operator="po_admin"):
        request = getattr(self.factory, method)(
            "/api/v3/projects/",
            HTTP_X_BKSOPS_ADMIN_READ=admin_header,
            HTTP_X_BKSOPS_AUDIT_OPERATOR=operator,
        )
        request.user = self.user
        request.app = SimpleNamespace(app_code="po-app")
        request._apigw_jwt_user_verified = True
        return request

    @mock.patch("gcloud.apigw.decorators.admin_read_app_whitelist.has", return_value=True)
    def test_verified_whitelist_request_enables_admin_read(self, whitelist_has):
        view = mark_admin_read_request()(lambda request: request.is_admin_read)
        self.assertTrue(view(self.build_request()))

    @mock.patch("gcloud.apigw.decorators.admin_read_app_whitelist.has", return_value=True)
    def test_audit_operator_mismatch_fails_closed(self, whitelist_has):
        view = mark_admin_read_request()(lambda request: True)
        response = view(self.build_request(operator="another_user"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)["code"], err_code.REQUEST_FORBIDDEN_INVALID.code)

    @mock.patch("gcloud.apigw.decorators.admin_read_app_whitelist.has", return_value=True)
    def test_unverified_apigw_user_fails_closed(self, whitelist_has):
        request = self.build_request()
        request._apigw_jwt_user_verified = False
        response = mark_admin_read_request()(lambda request: True)(request)
        self.assertEqual(json.loads(response.content)["code"], err_code.REQUEST_FORBIDDEN_INVALID.code)

    def test_absent_header_keeps_normal_mode(self):
        request = self.factory.get("/api/v3/projects/")
        request.user = self.user
        request.app = SimpleNamespace(app_code="not-used")
        request._apigw_jwt_user_verified = True
        result = mark_admin_read_request()(lambda request: request.is_admin_read)(request)
        self.assertFalse(result)

    @mock.patch("gcloud.apigw.decorators.admin_read_app_whitelist.has", return_value=True)
    def test_get_only_marker_rejects_post(self, whitelist_has):
        response = mark_admin_read_request()(lambda request: True)(self.build_request(method="post"))
        self.assertEqual(json.loads(response.content)["code"], err_code.REQUEST_FORBIDDEN_INVALID.code)


class AdminReadCacheKeyTestCase(TestCase):
    def test_admin_read_mode_changes_cache_key(self):
        request = RequestFactory().get("/api/v3/projects/1/")
        request.user = SimpleNamespace(username="po_admin")
        request.is_admin_read = False
        normal_key = api_hash_key(request)
        request.is_admin_read = True
        self.assertNotEqual(normal_key, api_hash_key(request))
