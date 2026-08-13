import json
from contextlib import ExitStack
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


class AdminReadInterceptorTestCase(TestCase):
    def build_request(self, template_source="project", is_admin_read=True):
        return SimpleNamespace(
            is_admin_read=is_admin_read,
            is_trust=False,
            user=SimpleNamespace(username="po_admin"),
            project=SimpleNamespace(id=1),
            GET={"template_source": template_source},
        )

    def assert_iam_calls(
        self, interceptor, module_path, kwargs=None, template_source="project", is_admin_read=True, expected_calls=0
    ):
        with ExitStack() as stack:
            allow = stack.enter_context(mock.patch("{}.allow_or_raise_auth_failed".format(module_path)))
            if module_path != "gcloud.iam_auth.view_interceptors.apigw.functionalization_task_view":
                stack.enter_context(mock.patch("{}.res_factory".format(module_path)))

            interceptor.process(self.build_request(template_source, is_admin_read), **(kwargs or {}))

            if expected_calls:
                allow.assert_called_once()
            else:
                allow.assert_not_called()

    def test_project_view_skips_iam(self):
        from gcloud.iam_auth.view_interceptors.apigw.project_view import ProjectViewInterceptor

        self.assert_iam_calls(
            ProjectViewInterceptor(), "gcloud.iam_auth.view_interceptors.apigw.project_view", {"project_id": 1}
        )

    def test_flow_view_skips_iam(self):
        from gcloud.iam_auth.view_interceptors.apigw.flow_view import FlowViewInterceptor

        self.assert_iam_calls(
            FlowViewInterceptor(), "gcloud.iam_auth.view_interceptors.apigw.flow_view", {"template_id": 1}
        )

    def test_business_template_info_skips_iam(self):
        from gcloud.iam_auth.view_interceptors.apigw.get_template_info import GetTemplateInfoInterceptor

        self.assert_iam_calls(
            GetTemplateInfoInterceptor(),
            "gcloud.iam_auth.view_interceptors.apigw.get_template_info",
            {"template_id": 1},
            template_source="business",
        )

    def test_task_view_skips_iam(self):
        from gcloud.iam_auth.view_interceptors.apigw.task_view import TaskViewInterceptor

        self.assert_iam_calls(
            TaskViewInterceptor(), "gcloud.iam_auth.view_interceptors.apigw.task_view", {"task_id": 1}
        )

    def test_function_view_skips_iam(self):
        from gcloud.iam_auth.view_interceptors.apigw.functionalization_task_view import FunctionViewInterceptor

        self.assert_iam_calls(
            FunctionViewInterceptor(), "gcloud.iam_auth.view_interceptors.apigw.functionalization_task_view"
        )

    def test_non_true_admin_read_keeps_iam_for_all_view_interceptors(self):
        from gcloud.iam_auth.view_interceptors.apigw.flow_view import FlowViewInterceptor
        from gcloud.iam_auth.view_interceptors.apigw.functionalization_task_view import FunctionViewInterceptor
        from gcloud.iam_auth.view_interceptors.apigw.get_template_info import GetTemplateInfoInterceptor
        from gcloud.iam_auth.view_interceptors.apigw.project_view import ProjectViewInterceptor
        from gcloud.iam_auth.view_interceptors.apigw.task_view import TaskViewInterceptor

        cases = (
            (
                "project",
                ProjectViewInterceptor(),
                "gcloud.iam_auth.view_interceptors.apigw.project_view",
                {"project_id": 1},
            ),
            ("flow", FlowViewInterceptor(), "gcloud.iam_auth.view_interceptors.apigw.flow_view", {"template_id": 1}),
            (
                "business_template",
                GetTemplateInfoInterceptor(),
                "gcloud.iam_auth.view_interceptors.apigw.get_template_info",
                {"template_id": 1},
            ),
            ("task", TaskViewInterceptor(), "gcloud.iam_auth.view_interceptors.apigw.task_view", {"task_id": 1}),
            (
                "function",
                FunctionViewInterceptor(),
                "gcloud.iam_auth.view_interceptors.apigw.functionalization_task_view",
                {},
            ),
        )

        for is_admin_read in (False, 1):
            for name, interceptor, module_path, kwargs in cases:
                with self.subTest(is_admin_read=is_admin_read, interceptor=name):
                    self.assert_iam_calls(
                        interceptor, module_path, kwargs, is_admin_read=is_admin_read, expected_calls=1
                    )

    def test_common_template_info_keeps_iam(self):
        from gcloud.iam_auth.view_interceptors.apigw.get_template_info import GetTemplateInfoInterceptor

        self.assert_iam_calls(
            GetTemplateInfoInterceptor(),
            "gcloud.iam_auth.view_interceptors.apigw.get_template_info",
            {"template_id": 1},
            template_source="common",
            expected_calls=1,
        )
