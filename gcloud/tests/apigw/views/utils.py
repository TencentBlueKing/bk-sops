# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import abc

from django.test import TestCase, Client
from django.conf import settings

from gcloud.tests.mock import *  # noqa
from gcloud.tests.mock_settings import *  # noqa

try:
    from bkoauth.decorators import apigw_required  # noqa

    BKOAUTH_DECORATOR_JWT_CLIENT = "bkoauth.decorators.JWTClient"
except ImportError:
    BKOAUTH_DECORATOR_JWT_CLIENT = "packages.bkoauth.decorators.JWTClient"

TEST_APP_CODE = "app_code"
TEST_USERNAME = ""


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


class APITest(TestCase, metaclass=abc.ABCMeta):
    def setUp(self):
        self.white_list_patcher = patch(APIGW_DECORATOR_CHECK_WHITE_LIST, MagicMock(return_value=True))

        self.dummy_user = MagicMock()
        self.dummy_user.username = ""
        self.user_cls = MagicMock()
        self.user_cls.objects = MagicMock()
        self.user_cls.objects.get_or_create = MagicMock(return_value=(self.dummy_user, False))

        self.get_user_model_patcher = patch(APIGW_DECORATOR_GET_USER_MODEL, MagicMock(return_value=self.user_cls))
        exist_return_true_qs = MagicMock()
        exist_return_true_qs.exist = MagicMock(return_value=True)
        self.project_filter_patcher = patch(PROJECT_FILTER, MagicMock(return_value=exist_return_true_qs))
        self.bkoauth_decorator_jwt_client = patch(
            BKOAUTH_DECORATOR_JWT_CLIENT,
            MagicMock(
                return_value=MockJwtClient(
                    {settings.APIGW_APP_CODE_KEY: TEST_APP_CODE, settings.APIGW_USER_USERNAME_KEY: TEST_USERNAME}
                )
            ),
        )

        self.white_list_patcher.start()
        self.get_user_model_patcher.start()
        self.project_filter_patcher.start()
        self.bkoauth_decorator_jwt_client.start()

        self.client = Client()

    def tearDown(self):
        self.white_list_patcher.stop()
        self.get_user_model_patcher.stop()
        self.project_filter_patcher.stop()
        self.bkoauth_decorator_jwt_client.stop()

    @abc.abstractmethod
    def url(sel):
        pass
