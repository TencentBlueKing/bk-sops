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

from django.conf import settings
from django.test import Client, TestCase

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
    request.user = MockJwtClientAttr(
        {
            settings.APIGW_MANAGER_USER_USERNAME_KEY: request.META.get("HTTP_BK_USERNAME", ""),
            "tenant_id": request.META.get("X-Bk-Tenant-Id", "system"),
        }
    )
    request.app = MockJwtClientAttr(
        {settings.APIGW_MANAGER_APP_CODE_KEY: request.META.get("HTTP_BK_APP_CODE", TEST_APP_CODE)}
    )
    return True


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

        settings.BK_APIGW_REQUIRE_EXEMPT = True

        self.client = Client()

    def tearDown(self):
        self.white_list_patcher.stop()
        self.project_filter_patcher.stop()
        self.inject_user.stop()

        settings.BK_APIGW_REQUIRE_EXEMPT = False

    @abc.abstractmethod
    def url(self):
        pass
