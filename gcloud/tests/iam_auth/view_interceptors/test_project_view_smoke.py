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
from unittest import TestCase, mock

from gcloud.contrib.appmaker import api as appmaker_api
from gcloud.taskflow3.apis.django import api as taskflow_api
from gcloud.taskflow3.apis.django.validators import QueryTaskCountValidator
from gcloud.tasktmpl3.apis.django import api as tasktmpl_api
from gcloud.tasktmpl3.apis.django.validators import GetTemplateCountValidator


class _SentinelDenied(Exception):
    """用于在测试中表明 interceptor 真的被调用且能阻断后续视图逻辑。"""


def _build_request(method="GET", body=b"{}"):
    return SimpleNamespace(
        method=method,
        GET={},
        POST={},
        FILES={},
        body=body,
        user=SimpleNamespace(username="tester"),
        META={},
    )


class ProjectInterceptorWiredOnViewsTestCase(TestCase):
    """对所有在本次修复中新接入 ``ProjectViewInterceptor`` /
    ``ProjectFlowCreateInterceptor`` 的 Django 函数视图做最小化"接线"冒烟测试。

    断言：当 interceptor.process 被设置为抛出哨兵异常时，请求会直接被该异常打断，
    说明 ``@iam_intercept(...)`` 已被正确地嵌进装饰器链；这样可以防御：
    - 装饰器顺序写错导致 IAM 检查被跳过；
    - 视图体里在 IAM 拒绝时仍发生数据库 / 远程查询副作用。

    对带 ``@request_validate(...)`` 的视图，我们把对应 Validator 临时打成放行，避免被
    validator 提前拦下从而无法触达 iam_intercept 层。
    """

    def _block(self, klass):
        return mock.patch(
            f"gcloud.iam_auth.view_interceptors.project.{klass}.process",
            side_effect=_SentinelDenied("denied"),
        )

    def test_taskflow_query_task_count_requires_project_view(self):
        request = _build_request(method="POST", body=b'{"conditions": {}, "group_by": "category"}')
        with mock.patch.object(QueryTaskCountValidator, "validate", return_value=(True, "")):
            with self._block("ProjectViewInterceptor"):
                with self.assertRaises(_SentinelDenied):
                    taskflow_api.query_task_count(request, project_id=1)

    def test_tasktmpl_get_template_count_requires_project_view(self):
        request = _build_request()
        with mock.patch.object(GetTemplateCountValidator, "validate", return_value=(True, "")):
            with self._block("ProjectViewInterceptor"):
                with self.assertRaises(_SentinelDenied):
                    tasktmpl_api.get_template_count(request, project_id=1)

    def test_tasktmpl_get_templates_with_expired_subprocess_requires_project_view(self):
        request = _build_request()
        with self._block("ProjectViewInterceptor"):
            with self.assertRaises(_SentinelDenied):
                tasktmpl_api.get_templates_with_expired_subprocess(request, project_id=1)

    def test_appmaker_get_appmaker_count_requires_project_view(self):
        request = _build_request()
        with self._block("ProjectViewInterceptor"):
            with self.assertRaises(_SentinelDenied):
                appmaker_api.get_appmaker_count(request, project_id=1)
