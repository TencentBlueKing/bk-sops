# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
import json

from mock import patch, MagicMock
from rest_framework.response import Response

from .base import LifeCycleHooksMixin


class LoginExemptMixin(LifeCycleHooksMixin):
    """蓝鲸登陆校验中间件豁免"""

    def setUp(self):
        patch("blueapps.account.middlewares.LoginRequiredMiddleware.process_view", MagicMock(return_value=None)).start()


class StandardResponseAssertionMixin:
    """校验接口响应是否正常并符合蓝鲸响应规范"""

    def _base_assertions(self, response):
        """
        :param response: 返回且返回字段符合蓝鲸规范
        :return: None
        """
        self.assertTrue(200 <= response.status_code <= 299)
        self.assertSetEqual(set(self._get_response_data(response).keys()), {"result", "data", "message", "code"})

    def assertStandardSuccessResponse(self, response):
        self._base_assertions(response)
        self.assertTrue(self._get_response_data(response).get("result"))

    def assertStandardFailResponse(self, response):
        self._base_assertions(response)
        self.assertFalse(self._get_response_data(response).get("result"))

    @staticmethod
    def _get_response_data(response):
        if isinstance(response, Response):
            return response.data
        return json.loads(response.content)
