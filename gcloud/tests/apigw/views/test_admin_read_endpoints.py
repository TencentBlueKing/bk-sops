# -*- coding: utf-8 -*-
import importlib
import json
from types import SimpleNamespace
from unittest import mock

from django.test import RequestFactory, SimpleTestCase

from gcloud import err_code
from gcloud.apigw.decorators import mark_admin_read_request, mark_request_whether_is_trust
from gcloud.taskflow3.models import TaskFlowInstance
from gcloud.tasktmpl3.models import TaskTemplate

GET_ADMIN_READ_VIEWS = (
    "get_template_list",
    "get_template_info",
    "get_template_schemes",
    "get_task_detail",
    "get_task_status",
    "get_task_node_data",
    "get_task_node_detail",
    "get_task_node_log",
    "get_functionalization_task_list",
)

MUTATING_VIEWS = (
    "create_and_start_task",
    "create_clocked_task",
    "create_periodic_task",
    "create_task",
    "create_template",
    "modify_constants_for_periodic_task",
    "modify_constants_for_task",
    "modify_cron_for_periodic_task",
    "modify_project_executor_proxy",
    "modify_template_executor_proxy",
    "modify_template_notify",
    "operate_node",
    "operate_task",
    "start_task",
)

ADMIN_READ_WRAPPER_CODE = mark_admin_read_request()(lambda request: None).__code__
TRUST_WRAPPER_CODE = mark_request_whether_is_trust(lambda request: None).__code__


def get_view(view_name):
    module = importlib.import_module("gcloud.apigw.views.{}".format(view_name))
    view = getattr(module, view_name)
    if hasattr(view, "cls") and hasattr(view.cls, "get"):
        handler = view.cls.get
        for cell in handler.__closure__ or ():
            if callable(cell.cell_contents):
                return cell.cell_contents
    return view


def wrapper_chain(view):
    chain = []
    while view is not None:
        chain.append(view)
        view = getattr(view, "__wrapped__", None)
    return chain


def find_wrapper(view, wrapper_code):
    for wrapper in wrapper_chain(view):
        if wrapper.__code__ is wrapper_code:
            return wrapper
    return None


class AdminReadEndpointAllowlistTestCase(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.project = SimpleNamespace(id=100, bk_biz_id=200)

    def build_request(self, method="get", path="/api/v3/read/", admin=True, body=None):
        headers = {}
        if admin:
            headers.update(
                {
                    "HTTP_X_BKSOPS_ADMIN_READ": "true",
                    "HTTP_X_BKSOPS_AUDIT_OPERATOR": "po_admin",
                }
            )
        if method == "post":
            request = self.factory.post(path, data=body or "{}", content_type="application/json", **headers)
        else:
            request = self.factory.get(path, **headers)
        request.user = SimpleNamespace(username="po_admin")
        request.app = SimpleNamespace(app_code="po-app")
        request._apigw_jwt_user_verified = True
        request.is_trust = False
        return request

    def invoke_admin_marker(self, view_name, request, **kwargs):
        marker = find_wrapper(get_view(view_name), ADMIN_READ_WRAPPER_CODE)
        self.assertIsNotNone(marker, "{} must opt in to admin read".format(view_name))
        return marker(request, **kwargs)

    def test_get_allowlist_installs_marker_immediately_after_trust_marker(self):
        for view_name in GET_ADMIN_READ_VIEWS:
            with self.subTest(view=view_name):
                chain = wrapper_chain(get_view(view_name))
                wrapper_codes = [wrapper.__code__ for wrapper in chain]
                self.assertIn(ADMIN_READ_WRAPPER_CODE, wrapper_codes)
                trust_index = wrapper_codes.index(TRUST_WRAPPER_CODE)
                self.assertEqual(wrapper_codes[trust_index + 1], ADMIN_READ_WRAPPER_CODE)

    def test_mutating_views_do_not_opt_in(self):
        for view_name in MUTATING_VIEWS:
            with self.subTest(view=view_name):
                self.assertIsNone(find_wrapper(get_view(view_name), ADMIN_READ_WRAPPER_CODE))

    @mock.patch("gcloud.apigw.decorators.admin_read_app_whitelist.has", return_value=True)
    @mock.patch("gcloud.apigw.decorators.get_project_with")
    @mock.patch("gcloud.apigw.views.preview_task_tree.preview_template_tree", return_value="preview")
    def test_preview_marker_accepts_admin_post_and_keeps_ordinary_post(self, preview, get_project, whitelist_has):
        get_project.return_value = self.project
        for admin in (True, False):
            with self.subTest(admin=admin):
                request = self.build_request(method="post", admin=admin, body=json.dumps({}))
                if not admin:
                    request.is_trust = True
                result = self.invoke_admin_marker("preview_task_tree", request, project_id="200", template_id="1")
                self.assertTrue(result["result"])
                self.assertEqual(result["data"], "preview")
                self.assertIs(request.is_admin_read, admin)

    @mock.patch("gcloud.apigw.decorators.admin_read_app_whitelist.has", return_value=True)
    def test_preview_marker_rejects_admin_get(self, whitelist_has):
        request = self.build_request(method="get")
        response = self.invoke_admin_marker("preview_task_tree", request, project_id="200", template_id="1")
        self.assertEqual(json.loads(response.content)["code"], err_code.REQUEST_FORBIDDEN_INVALID.code)

    @mock.patch("gcloud.apigw.decorators.admin_read_app_whitelist.has", return_value=True)
    @mock.patch("gcloud.apigw.decorators.get_project_with")
    @mock.patch("gcloud.apigw.views.get_template_info.format_template_data")
    @mock.patch("gcloud.apigw.views.get_template_info.TaskTemplate.objects.select_related")
    def test_template_admin_read_reaches_view(self, select_related, format_template_data, get_project, whitelist_has):
        get_project.return_value = self.project
        select_related.return_value.get.return_value = SimpleNamespace()
        format_template_data.return_value = {"pipeline_tree": {}, "name": "template"}

        result = self.invoke_admin_marker("get_template_info", self.build_request(), template_id="1", project_id="200")

        self.assertTrue(result["result"])
        self.assertEqual(result["data"]["name"], "template")

    @mock.patch("gcloud.apigw.decorators.admin_read_app_whitelist.has", return_value=True)
    @mock.patch("gcloud.apigw.decorators.get_project_with")
    @mock.patch("gcloud.apigw.views.get_template_info.TaskTemplate.objects.select_related")
    def test_template_admin_read_keeps_project_ownership_filter(self, select_related, get_project, whitelist_has):
        get_project.return_value = self.project

        def reject_cross_project_template(**filters):
            self.assertEqual(filters, {"id": "1", "project_id": 100, "is_deleted": False})
            raise TaskTemplate.DoesNotExist()

        select_related.return_value.get.side_effect = reject_cross_project_template
        result = self.invoke_admin_marker("get_template_info", self.build_request(), template_id="1", project_id="200")

        self.assertFalse(result["result"])
        self.assertEqual(result["code"], err_code.CONTENT_NOT_EXIST.code)

    @mock.patch("gcloud.apigw.decorators.admin_read_app_whitelist.has", return_value=True)
    @mock.patch("gcloud.apigw.decorators.get_project_with")
    @mock.patch("gcloud.apigw.views.get_task_detail.TaskFlowInstance.objects.get")
    def test_task_admin_read_reaches_view(self, get_task, get_project, whitelist_has):
        get_project.return_value = self.project
        get_task.return_value = SimpleNamespace(get_task_detail=lambda: "task detail")

        result = self.invoke_admin_marker("get_task_detail", self.build_request(), task_id="3", project_id="200")

        self.assertTrue(result["result"])
        self.assertEqual(result["data"], "task detail")

    @mock.patch("gcloud.apigw.decorators.admin_read_app_whitelist.has", return_value=True)
    @mock.patch("gcloud.apigw.decorators.get_project_with")
    @mock.patch("gcloud.apigw.views.get_task_detail.TaskFlowInstance.objects.get")
    def test_task_admin_read_keeps_project_ownership_filter(self, get_task, get_project, whitelist_has):
        get_project.return_value = self.project

        def reject_cross_project_task(**filters):
            self.assertEqual(filters, {"id": "2", "project_id": 100})
            raise TaskFlowInstance.DoesNotExist()

        get_task.side_effect = reject_cross_project_task
        result = self.invoke_admin_marker("get_task_detail", self.build_request(), task_id="2", project_id="200")

        self.assertFalse(result["result"])
        self.assertEqual(result["code"], err_code.CONTENT_NOT_EXIST.code)

    @mock.patch("gcloud.apigw.decorators.admin_read_app_whitelist.has", return_value=True)
    @mock.patch("gcloud.apigw.decorators.get_project_with")
    @mock.patch("gcloud.apigw.views.get_task_node_detail.TaskFlowInstance.objects.get")
    def test_node_admin_read_reaches_view(self, get_task, get_project, whitelist_has):
        get_project.return_value = self.project
        get_task.return_value = SimpleNamespace(
            get_node_detail=lambda **kwargs: {"result": True, "data": {"node": kwargs["node_id"]}}
        )
        request = self.build_request(path="/api/v3/node/?node_id=node-1")

        result = self.invoke_admin_marker("get_task_node_detail", request, task_id="2", project_id="200")

        self.assertTrue(result["result"])
        self.assertEqual(result["data"], {"node": "node-1"})

    @mock.patch("gcloud.apigw.decorators.admin_read_app_whitelist.has", return_value=True)
    @mock.patch("gcloud.apigw.decorators.get_project_with")
    @mock.patch("gcloud.apigw.views.get_task_node_detail.TaskFlowInstance.objects.get")
    def test_node_admin_read_keeps_project_ownership_filter(self, get_task, get_project, whitelist_has):
        get_project.return_value = self.project

        def reject_cross_project_task(**filters):
            self.assertEqual(filters, {"id": "2", "project_id": 100})
            raise TaskFlowInstance.DoesNotExist()

        get_task.side_effect = reject_cross_project_task
        request = self.build_request(path="/api/v3/node/?node_id=node-1")
        result = self.invoke_admin_marker("get_task_node_detail", request, task_id="2", project_id="200")

        self.assertFalse(result["result"])
        self.assertEqual(result["code"], err_code.CONTENT_NOT_EXIST.code)
