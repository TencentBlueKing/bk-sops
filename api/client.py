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

from django.conf import settings
from django.utils import translation

from . import http


class BKComponentClient(object):
    def __init__(self, username, language=None, use_test_env=False, app_code=None, app_secret=None):
        self.username = username
        self.language = language or translation.get_language()
        self.use_test_env = use_test_env
        self.app_code = app_code or settings.APP_CODE
        self.app_secret = app_secret or settings.SECRET_KEY

    def _pre_process_headers(self, headers):
        if not headers:
            headers = {
                "Content-Type": "application/json",
                "blueking-language": self.language,
            }
        else:
            headers["blueking-language"] = self.language

        if self.use_test_env:
            headers["x-use-test-env"] = "1"

        return headers

    def _pre_process_data(self, data):
        data["bk_username"] = self.username
        data["bk_app_code"] = self.app_code
        data["bk_app_secret"] = self.app_secret

    def _request(self, method, url, data, headers=None, verify=False, cert=None, timeout=None, cookies=None):

        headers = headers or {}
        self._pre_process_headers(headers)

        self._pre_process_data(data)

        return getattr(http, method.lower())(
            url=url, data=data, headers=headers, verify=verify, cert=cert, timeout=timeout, cookies=cookies
        )
