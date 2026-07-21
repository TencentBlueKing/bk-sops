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
from unittest import mock, skipUnless

from django.test import TestCase

try:
    import pipeline.contrib.diagnostics  # noqa: F401

    DIAGNOSTICS_AVAILABLE = True
except ImportError:
    DIAGNOSTICS_AVAILABLE = False

_SUPP = "gcloud.contrib.admin.diagnostics.supplement"


@skipUnless(DIAGNOSTICS_AVAILABLE, "pipeline.contrib.diagnostics unavailable (requires bamboo-pipeline>=3.24.12)")
class SupplementScanTest(TestCase):
    def test_running_task_without_live_process_is_flagged(self):
        with mock.patch(_SUPP + "._running_root_ids", return_value=["root-run"]), mock.patch(
            _SUPP + "._has_live_process", return_value=False
        ), mock.patch(_SUPP + ".upsert_case", return_value=mock.MagicMock()) as m_upsert:
            from gcloud.contrib.admin.diagnostics.supplement import scan_running_tasks_without_live_process

            cases = scan_running_tasks_without_live_process(batch=10)

        self.assertTrue(m_upsert.called)
        self.assertEqual(len(cases), 1)

    def test_running_task_with_live_process_is_not_flagged(self):
        with mock.patch(_SUPP + "._running_root_ids", return_value=["root-run"]), mock.patch(
            _SUPP + "._has_live_process", return_value=True
        ), mock.patch(_SUPP + ".upsert_case") as m_upsert:
            from gcloud.contrib.admin.diagnostics.supplement import scan_running_tasks_without_live_process

            cases = scan_running_tasks_without_live_process(batch=10)

        self.assertFalse(m_upsert.called)
        self.assertEqual(cases, [])

    def test_no_running_tasks_produces_no_cases(self):
        with mock.patch(_SUPP + "._running_root_ids", return_value=[]), mock.patch(_SUPP + ".upsert_case") as m_upsert:
            from gcloud.contrib.admin.diagnostics.supplement import scan_running_tasks_without_live_process

            cases = scan_running_tasks_without_live_process()

        self.assertFalse(m_upsert.called)
        self.assertEqual(cases, [])
