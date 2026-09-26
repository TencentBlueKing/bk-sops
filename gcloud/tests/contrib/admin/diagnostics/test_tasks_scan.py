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
from unittest import mock

from django.test import TestCase, override_settings
from fakeredis import FakeRedis

from gcloud.contrib.admin import tasks


class ScanTaskTest(TestCase):
    @override_settings(redis_inst=FakeRedis())
    def test_scan_calls_scanner_when_lock_acquired(self):
        with mock.patch.object(tasks, "scan_stalled_roots", return_value=[]) as m_scan, mock.patch(
            "gcloud.contrib.admin.diagnostics.supplement.scan_running_tasks_without_live_process",
            return_value=[],
        ) as m_supp, mock.patch(
            "gcloud.contrib.admin.diagnostics.supplement.close_recovered_cases", return_value=(0, 0)
        ) as m_close:
            tasks.scan_stuck_diagnostics()
        self.assertTrue(m_scan.called)
        self.assertTrue(m_supp.called)
        self.assertTrue(m_close.called)

    @override_settings(redis_inst=FakeRedis())
    def test_scan_skips_when_lock_busy(self):
        # 预占单例锁，模拟另一个 worker 正在执行
        from django.conf import settings

        settings.redis_inst.set(name=tasks._SCAN_LOCK_KEY, value="other", nx=True, ex=60)
        with mock.patch.object(tasks, "scan_stalled_roots", return_value=[]) as m_scan:
            tasks.scan_stuck_diagnostics()
        self.assertFalse(m_scan.called)

    @override_settings(redis_inst=FakeRedis())
    def test_scan_releases_lock_after_run(self):
        from django.conf import settings

        with mock.patch.object(tasks, "scan_stalled_roots", return_value=[]), mock.patch(
            "gcloud.contrib.admin.diagnostics.supplement.scan_running_tasks_without_live_process",
            return_value=[],
        ), mock.patch("gcloud.contrib.admin.diagnostics.supplement.close_recovered_cases", return_value=(0, 0)):
            tasks.scan_stuck_diagnostics()
        # 运行结束后锁应被释放，下一轮可再次抢到
        self.assertIsNone(settings.redis_inst.get(tasks._SCAN_LOCK_KEY))

    def test_scan_noop_when_scanner_unavailable(self):
        with mock.patch.object(tasks, "scan_stalled_roots", None):
            # scanner 不可用时应直接返回，不触碰 redis
            tasks.scan_stuck_diagnostics()

    @override_settings(redis_inst=FakeRedis())
    def test_supplement_failure_does_not_break_scan(self):
        with mock.patch.object(tasks, "scan_stalled_roots", return_value=[]) as m_scan, mock.patch(
            "gcloud.contrib.admin.diagnostics.supplement.scan_running_tasks_without_live_process",
            side_effect=Exception("boom"),
        ):
            tasks.scan_stuck_diagnostics()
        self.assertTrue(m_scan.called)

    @override_settings(redis_inst=FakeRedis())
    def test_case_close_failure_does_not_break_scan(self):
        with mock.patch.object(tasks, "scan_stalled_roots", return_value=[]) as m_scan, mock.patch(
            "gcloud.contrib.admin.diagnostics.supplement.scan_running_tasks_without_live_process",
            return_value=[],
        ), mock.patch(
            "gcloud.contrib.admin.diagnostics.supplement.close_recovered_cases", side_effect=Exception("boom")
        ):
            tasks.scan_stuck_diagnostics()
        self.assertTrue(m_scan.called)

    @override_settings(redis_inst=FakeRedis())
    def test_root_scan_failure_still_runs_supplement_and_close(self):
        from django.conf import settings

        with mock.patch.object(tasks, "scan_stalled_roots", side_effect=Exception("boom")), mock.patch(
            "gcloud.contrib.admin.diagnostics.supplement.scan_running_tasks_without_live_process",
            return_value=[],
        ) as m_supp, mock.patch(
            "gcloud.contrib.admin.diagnostics.supplement.close_recovered_cases", return_value=(0, 0)
        ) as m_close:
            tasks.scan_stuck_diagnostics()
        self.assertTrue(m_supp.called)
        self.assertTrue(m_close.called)
        self.assertIsNone(settings.redis_inst.get(tasks._SCAN_LOCK_KEY))


def _supplement_patches():
    return (
        mock.patch(
            "gcloud.contrib.admin.diagnostics.supplement.scan_running_tasks_without_live_process", return_value=[]
        ),
        mock.patch("gcloud.contrib.admin.diagnostics.supplement.close_recovered_cases", return_value=(0, 0)),
    )


class RootScanSelectionTest(TestCase):
    @override_settings(redis_inst=FakeRedis(), PIPELINE_DIAGNOSTICS_WINDOW_SCAN_ENABLED=True)
    def test_window_scan_replaces_sampling_when_enabled(self):
        supp, close = _supplement_patches()
        with mock.patch.object(
            tasks, "scan_silence_windows", return_value=[SimpleNamespace(cases=2)]
        ) as m_window, mock.patch.object(
            tasks, "scan_stalled_roots", return_value=[]
        ) as m_scan, supp as m_supp, close as m_close:
            tasks.scan_stuck_diagnostics()
        self.assertTrue(m_window.called)
        self.assertFalse(m_scan.called)
        self.assertTrue(m_supp.called)
        self.assertTrue(m_close.called)

    @override_settings(redis_inst=FakeRedis(), PIPELINE_DIAGNOSTICS_WINDOW_SCAN_ENABLED=False)
    def test_sampling_scan_is_kept_when_window_disabled(self):
        supp, close = _supplement_patches()
        with mock.patch.object(tasks, "scan_silence_windows") as m_window, mock.patch.object(
            tasks, "scan_stalled_roots", return_value=[]
        ) as m_scan, supp, close:
            tasks.scan_stuck_diagnostics()
        self.assertFalse(m_window.called)
        self.assertTrue(m_scan.called)

    @override_settings(redis_inst=FakeRedis(), PIPELINE_DIAGNOSTICS_WINDOW_SCAN_ENABLED=True)
    def test_falls_back_to_sampling_on_old_engine(self):
        supp, close = _supplement_patches()
        with mock.patch.object(tasks, "scan_silence_windows", None), mock.patch.object(
            tasks, "scan_stalled_roots", return_value=[]
        ) as m_scan, supp, close:
            tasks.scan_stuck_diagnostics()
        self.assertTrue(m_scan.called)


class SignatureTaskTest(TestCase):
    @override_settings(redis_inst=FakeRedis(), PIPELINE_DIAGNOSTICS_SIGNATURE_SCAN_ENABLED=True)
    def test_runs_when_enabled(self):
        with mock.patch.object(tasks, "scan_signatures", return_value=[]) as m_scan:
            tasks.scan_stuck_signatures()
        self.assertTrue(m_scan.called)

    @override_settings(redis_inst=FakeRedis(), PIPELINE_DIAGNOSTICS_SIGNATURE_SCAN_ENABLED=False)
    def test_noop_when_disabled(self):
        with mock.patch.object(tasks, "scan_signatures") as m_scan, mock.patch.object(
            tasks, "_acquire_singleflight"
        ) as m_lock:
            tasks.scan_stuck_signatures()
        self.assertFalse(m_scan.called)
        m_lock.assert_not_called()

    @override_settings(redis_inst=FakeRedis(), PIPELINE_DIAGNOSTICS_SIGNATURE_SCAN_ENABLED=True)
    def test_skips_when_lock_busy(self):
        from django.conf import settings

        settings.redis_inst.set(name=tasks._SIGNATURE_LOCK_KEY, value="other", nx=True, ex=60)
        with mock.patch.object(tasks, "scan_signatures") as m_scan:
            tasks.scan_stuck_signatures()
        self.assertFalse(m_scan.called)

    @override_settings(redis_inst=FakeRedis(), PIPELINE_DIAGNOSTICS_SIGNATURE_SCAN_ENABLED=True)
    def test_failure_releases_lock(self):
        from django.conf import settings

        with mock.patch.object(tasks, "scan_signatures", side_effect=Exception("boom")):
            tasks.scan_stuck_signatures()
        self.assertIsNone(settings.redis_inst.get(tasks._SIGNATURE_LOCK_KEY))


class CallbackTaskTest(TestCase):
    @override_settings(redis_inst=FakeRedis(), PIPELINE_DIAGNOSTICS_CALLBACK_SCAN_ENABLED=True)
    def test_runs_when_enabled(self):
        with mock.patch.object(tasks, "scan_callbacks", return_value=None) as m_scan:
            tasks.scan_stuck_callbacks()
        self.assertTrue(m_scan.called)

    @override_settings(redis_inst=FakeRedis(), PIPELINE_DIAGNOSTICS_CALLBACK_SCAN_ENABLED=False)
    def test_noop_when_disabled(self):
        with mock.patch.object(tasks, "scan_callbacks") as m_scan, mock.patch.object(
            tasks, "_acquire_singleflight"
        ) as m_lock:
            tasks.scan_stuck_callbacks()
        self.assertFalse(m_scan.called)
        m_lock.assert_not_called()

    @override_settings(PIPELINE_DIAGNOSTICS_CALLBACK_SCAN_ENABLED=True)
    def test_noop_on_old_engine(self):
        with mock.patch.object(tasks, "scan_callbacks", None), mock.patch.object(
            tasks, "_acquire_singleflight"
        ) as m_lock:
            tasks.scan_stuck_callbacks()
        m_lock.assert_not_called()
