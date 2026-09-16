# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import abc
from types import SimpleNamespace

from django.conf import settings
from django.test import Client, TestCase

from gcloud.iam_auth import IAMMeta
from gcloud.iam_auth.models import Resource
from gcloud.iam_auth.topology import project_path
from gcloud.tests.mock import *  # noqa
from gcloud.tests.mock_settings import *  # noqa

TEST_APP_CODE = "app_code"
TEST_USERNAME = "tester"


def dummy_params_wrapper(perm):
    def inner_dummy_wrapper(func):
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    return inner_dummy_wrapper


def dummy_wrapper(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


def mock_inject_user(request):
    return


def mock_check_white_apps(request):
    if not getattr(getattr(request, "user", None), "is_authenticated", False):
        request.user = MockJwtClientAttr(
            {
                settings.APIGW_MANAGER_USER_USERNAME_KEY: request.META.get("HTTP_BK_USERNAME", ""),
                "tenant_id": request.META.get("HTTP_X_BK_TENANT_ID", "system"),
            }
        )
    request.app = MockJwtClientAttr(
        {settings.APIGW_MANAGER_APP_CODE_KEY: request.META.get("HTTP_BK_APP_CODE", TEST_APP_CODE)}
    )
    return True


def mock_tenant_local_resource(request, resource_type, resource_id):
    """Represent a resource already resolved inside the request tenant.

    Legacy APIGW business tests mock their domain managers instead of creating
    IAM-backed database objects. Dedicated IAM V4 tests exercise the real
    tenant loader; these tests only need a valid resource to reach the business
    behavior under test.
    """

    attributes = {"name": "test-resource"}
    project = getattr(request, "project", None)
    if resource_type not in {IAMMeta.PROJECT_RESOURCE, IAMMeta.COMMON_FLOW_RESOURCE} and project is not None:
        attributes["_bk_iam_path_"] = project_path(project.id)
    return Resource(IAMMeta.SYSTEM_ID, resource_type, str(resource_id), attributes)


RESOURCE_LOADER_MODULES = (
    "task_operate",
    "task_edit",
    "claim_functionalization_task",
    "fast_create_task",
    "get_periodic_task_info",
    "flow_view",
    "get_template_info",
    "create_task",
    "modify_template_notify",
    "create_periodic_task",
    "periodic_task_edit",
    "template_edit",
    "task_view",
    "common_flow_view",
)


class MockApiGatewayJWTPayloadMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        username_header = "HTTP_BK_JWT_USERNAME"
        verified_header = "HTTP_BK_JWT_USER_VERIFIED"
        if username_header in request.META or verified_header in request.META:
            jwt_user = {}
            if username_header in request.META:
                jwt_user[settings.APIGW_MANAGER_USER_USERNAME_KEY] = request.META[username_header]
            if verified_header in request.META:
                jwt_user["verified"] = request.META[verified_header]
            request.jwt = SimpleNamespace(payload={"user": jwt_user})
        return self.get_response(request)


class APITest(TestCase, metaclass=abc.ABCMeta):
    def setUp(self):
        self.white_list_patcher = patch(APIGW_DECORATOR_CHECK_WHITE_LIST, mock_check_white_apps)
        self.inject_user = patch(APIGW_DECORATOR_INJECT_USER, mock_inject_user)
        self.dummy_user = MagicMock()
        self.dummy_user.username = ""
        self.user_cls = MagicMock()
        self.user_cls.objects = MagicMock()
        self.user_cls.objects.get_or_create = MagicMock(return_value=(self.dummy_user, False))

        exist_return_true_qs = MagicMock()
        exist_return_true_qs.exist = MagicMock(return_value=True)
        self.project_filter_patcher = patch(PROJECT_FILTER, MagicMock(return_value=exist_return_true_qs))

        self.white_list_patcher.start()
        self.project_filter_patcher.start()
        self.inject_user.start()
        self.resource_loader_patchers = [
            patch(
                "gcloud.iam_auth.view_interceptors.apigw.{}.load_resource_for_request".format(module),
                mock_tenant_local_resource,
            )
            for module in RESOURCE_LOADER_MODULES
        ]
        for patcher in self.resource_loader_patchers:
            patcher.start()

        settings.BK_APIGW_REQUIRE_EXEMPT = True

        self.client = Client()

    def tearDown(self):
        for patcher in self.resource_loader_patchers:
            patcher.stop()
        self.white_list_patcher.stop()
        self.project_filter_patcher.stop()
        self.inject_user.stop()

        settings.BK_APIGW_REQUIRE_EXEMPT = False

    @abc.abstractmethod
    def url(self):
        pass
