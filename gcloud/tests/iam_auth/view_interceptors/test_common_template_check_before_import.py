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

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.test import TestCase
from iam.exceptions import AuthFailedException

from gcloud.iam_auth.view_interceptors.common_template import CheckBeforeImportInterceptor

IAM_IS_ALLOWED = "gcloud.iam_auth.view_interceptors.common_template.iam.is_allowed"


class CheckBeforeImportInterceptorTest(TestCase):
    """BAC: 公共流程导入前置检测接口必须与正式导入一致要求 COMMON_FLOW_CREATE，
    避免无任何公共流程权限的用户借预检接口探测导入冲突/覆盖信息。"""

    def setUp(self):
        self.interceptor = CheckBeforeImportInterceptor()
        self.request = SimpleNamespace(user=SimpleNamespace(username="tester"))

    def test_denies_without_common_flow_create(self):
        with patch(IAM_IS_ALLOWED, MagicMock(return_value=False)):
            with self.assertRaises(AuthFailedException):
                self.interceptor.process(self.request)

    def test_allows_with_common_flow_create(self):
        with patch(IAM_IS_ALLOWED, MagicMock(return_value=True)):
            # 不抛异常即视为通过
            self.interceptor.process(self.request)
