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
from unittest import mock, skipUnless

from django.test import RequestFactory, TestCase

try:
    import pipeline.contrib.diagnostics  # noqa: F401

    DIAGNOSTICS_AVAILABLE = True
except ImportError:
    DIAGNOSTICS_AVAILABLE = False

_INTERCEPTOR = "gcloud.iam_auth.view_interceptors.admin.AdminViewViewInterceptor.process"


def _superuser_request(path, **params):
    factory = RequestFactory()
    request = factory.get(path, data=params)
    request.user = mock.MagicMock(is_superuser=True, username="admin")
    return request


@skipUnless(DIAGNOSTICS_AVAILABLE, "pipeline.contrib.diagnostics unavailable (requires bamboo-pipeline>=3.24.12)")
class DiagnosticCaseViewTest(TestCase):
    def setUp(self):
        from pipeline.contrib.diagnostics.models import DiagnosticCase

        self.model = DiagnosticCase
        self.open_case = DiagnosticCase.objects.create(
            root_pipeline_id="root-open",
            node_id="n1",
            stuck_type="stalled_no_progress",
            severity=DiagnosticCase.SEVERITY_WARNING,
            status=DiagnosticCase.STATUS_OPEN,
            evidence={"stall_seconds": 3600},
        )
        DiagnosticCase.objects.create(
            root_pipeline_id="root-resolved",
            node_id="n2",
            stuck_type="stalled_no_progress",
            severity=DiagnosticCase.SEVERITY_INFO,
            status=DiagnosticCase.STATUS_RESOLVED,
        )

    def test_case_list_returns_paginated_json(self):
        from gcloud.contrib.admin.views import diagnostics

        with mock.patch(_INTERCEPTOR):
            resp = diagnostics.diagnostic_case_list(_superuser_request("/admin/diagnostics/cases/"))

        body = json.loads(resp.content)
        self.assertTrue(body["result"])
        self.assertEqual(body["data"]["total"], 2)
        self.assertEqual(len(body["data"]["items"]), 2)

    def test_case_list_filter_by_status(self):
        from gcloud.contrib.admin.views import diagnostics

        with mock.patch(_INTERCEPTOR):
            resp = diagnostics.diagnostic_case_list(_superuser_request("/admin/diagnostics/cases/", status="open"))

        body = json.loads(resp.content)
        self.assertEqual(body["data"]["total"], 1)
        self.assertEqual(body["data"]["items"][0]["root_pipeline_id"], "root-open")
        self.assertEqual(body["data"]["items"][0]["stall_seconds"], 3600)

    def test_case_list_forbidden_for_non_superuser(self):
        from gcloud.contrib.admin.views import diagnostics

        request = _superuser_request("/admin/diagnostics/cases/")
        request.user = mock.MagicMock(is_superuser=False, username="normal")
        with mock.patch(_INTERCEPTOR):
            resp = diagnostics.diagnostic_case_list(request)
        self.assertEqual(resp.status_code, 403)

    def test_case_detail_returns_full_case(self):
        from gcloud.contrib.admin.views import diagnostics

        with mock.patch(_INTERCEPTOR):
            resp = diagnostics.diagnostic_case_detail(
                _superuser_request("/admin/diagnostics/cases/detail/", case_id=self.open_case.id)
            )

        body = json.loads(resp.content)
        self.assertTrue(body["result"])
        self.assertEqual(body["data"]["id"], self.open_case.id)
        self.assertEqual(body["data"]["evidence"], {"stall_seconds": 3600})

    def test_case_detail_missing_case_id(self):
        from gcloud.contrib.admin.views import diagnostics

        with mock.patch(_INTERCEPTOR):
            resp = diagnostics.diagnostic_case_detail(_superuser_request("/admin/diagnostics/cases/detail/"))

        body = json.loads(resp.content)
        self.assertFalse(body["result"])
        self.assertEqual(body["message"], "case_id is required")


@skipUnless(DIAGNOSTICS_AVAILABLE, "pipeline.contrib.diagnostics unavailable (requires bamboo-pipeline>=3.24.12)")
class FailedParkedFilterTest(TestCase):
    """节点失败等人工(FAILED 停靠)默认从'卡住'视图排除，开关/显式筛选可查看。"""

    def setUp(self):
        from pipeline.contrib.diagnostics.models import DiagnosticCase

        self.model = DiagnosticCase
        # 预期内失败态：应默认隐藏
        DiagnosticCase.objects.create(
            root_pipeline_id="root-failed",
            node_id="nf",
            stuck_type="process_alive_but_terminal_state",
            severity=DiagnosticCase.SEVERITY_CRITICAL,
            status=DiagnosticCase.STATUS_OPEN,
            message="Process 1 is alive while node nf is in terminal state FAILED",
        )
        # 真异常：FINISHED 终态仍存活，不应被隐藏
        DiagnosticCase.objects.create(
            root_pipeline_id="root-finished",
            node_id="ni",
            stuck_type="process_alive_but_terminal_state",
            severity=DiagnosticCase.SEVERITY_CRITICAL,
            status=DiagnosticCase.STATUS_OPEN,
            message="Process 2 is alive while node ni is in terminal state FINISHED",
        )
        # 其它类型不受影响
        DiagnosticCase.objects.create(
            root_pipeline_id="root-other",
            node_id="no",
            stuck_type="stalled_no_progress",
            severity=DiagnosticCase.SEVERITY_WARNING,
            status=DiagnosticCase.STATUS_OPEN,
        )

    def _list(self, **params):
        from gcloud.contrib.admin.views import diagnostics

        with mock.patch(_INTERCEPTOR):
            resp = diagnostics.diagnostic_case_list(_superuser_request("/admin/diagnostics/cases/", **params))
        return json.loads(resp.content)["data"]

    def test_failed_parked_hidden_by_default(self):
        data = self._list()
        roots = {it["root_pipeline_id"] for it in data["items"]}
        self.assertEqual(data["total"], 2)
        self.assertEqual(data["hidden_failed_parked"], 1)
        self.assertNotIn("root-failed", roots)
        self.assertIn("root-finished", roots)
        self.assertIn("root-other", roots)

    def test_include_flag_shows_failed_parked(self):
        data = self._list(include_failed_parked="1")
        roots = {it["root_pipeline_id"] for it in data["items"]}
        self.assertEqual(data["total"], 3)
        self.assertEqual(data["hidden_failed_parked"], 0)
        self.assertIn("root-failed", roots)

    def test_explicit_stuck_type_filter_not_auto_excluded(self):
        data = self._list(stuck_type="process_alive_but_terminal_state")
        roots = {it["root_pipeline_id"] for it in data["items"]}
        self.assertEqual(data["total"], 2)
        self.assertEqual(data["hidden_failed_parked"], 0)
        self.assertIn("root-failed", roots)
        self.assertIn("root-finished", roots)
