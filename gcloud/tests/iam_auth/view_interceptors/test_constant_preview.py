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

import json
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.test import TestCase
from iam.exceptions import AuthFailedException

from gcloud.core.models import Project
from gcloud.iam_auth.view_interceptors.template import ConstantPreviewInterceptor

GET_IAM_CLIENT = "gcloud.iam_auth.view_interceptors.template.get_iam_client"
RES_FOR_PROJECT = "gcloud.iam_auth.view_interceptors.template.res_factory.resources_for_project"
TENANT_ID = "default"


def _make_request(body_obj=None, raw_body=None):
    if raw_body is not None:
        body = raw_body
    else:
        body = json.dumps(body_obj or {}).encode("utf-8")
    return SimpleNamespace(user=SimpleNamespace(username="tester", tenant_id=TENANT_ID), body=body)


def _patch_iam_allowed(allowed):
    """拦截器按租户动态取 IAM client，因此从 get_iam_client 处注入判定结果。"""
    return patch(GET_IAM_CLIENT, MagicMock(return_value=MagicMock(is_allowed=MagicMock(return_value=allowed))))


class ConstantPreviewInterceptorTest(TestCase):
    """BAC: 变量预览接口必须按项目/公共流程补齐鉴权, 否则任意登录用户均可触发
    web 进程内的 Mako 渲染(叠加模板注入即 RCE)。"""

    def setUp(self):
        self.interceptor = ConstantPreviewInterceptor()

    @patch(RES_FOR_PROJECT, MagicMock(return_value=[]))
    def test_project_denied_without_flow_create(self):
        request = _make_request({"constants": {}, "extra_data": {"project_id": 1}})
        with _patch_iam_allowed(False):
            with self.assertRaises(AuthFailedException):
                self.interceptor.process(request)

    @patch(RES_FOR_PROJECT, MagicMock(return_value=[]))
    def test_project_allowed_with_flow_create(self):
        request = _make_request({"constants": {}, "extra_data": {"project_id": 1}})
        with _patch_iam_allowed(True):
            self.interceptor.process(request)

    def test_common_denied_without_common_flow_create(self):
        request = _make_request({"constants": {}, "extra_data": {}})
        with _patch_iam_allowed(False):
            with self.assertRaises(AuthFailedException):
                self.interceptor.process(request)

    def test_common_allowed_with_common_flow_create(self):
        request = _make_request({"constants": {}, "extra_data": {}})
        with _patch_iam_allowed(True):
            self.interceptor.process(request)

    def test_malformed_body_denied(self):
        request = _make_request(raw_body=b"not-a-json")
        with _patch_iam_allowed(True):
            with self.assertRaises(AuthFailedException):
                self.interceptor.process(request)

    def test_nonexistent_project_denied(self):
        request = _make_request({"constants": {}, "extra_data": {"project_id": 999999}})
        with patch(RES_FOR_PROJECT, MagicMock(side_effect=Project.DoesNotExist)):
            with _patch_iam_allowed(True):
                with self.assertRaises(AuthFailedException):
                    self.interceptor.process(request)
