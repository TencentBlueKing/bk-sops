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
import datetime
from unittest import mock, skipUnless

import factory
from django.db.models import signals
from django.test import TestCase
from django.utils import timezone

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
            _SUPP + "._roots_with_live_process", return_value=set()
        ), mock.patch(_SUPP + "._still_running", return_value=True), mock.patch(
            _SUPP + ".upsert_case", return_value=mock.MagicMock()
        ) as m_upsert:
            from gcloud.contrib.admin.diagnostics.supplement import scan_running_tasks_without_live_process

            cases = scan_running_tasks_without_live_process(batch=10)

        self.assertTrue(m_upsert.called)
        self.assertEqual(len(cases), 1)

    def test_running_task_with_live_process_is_not_flagged(self):
        with mock.patch(_SUPP + "._running_root_ids", return_value=["root-run"]), mock.patch(
            _SUPP + "._roots_with_live_process", return_value={"root-run"}
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


class DiagnosticsDataMixin(object):
    """造真实数据：Project / PipelineInstance / TaskFlowInstance / eri Process。"""

    # PipelineInstance 与 TaskFlowInstance 的 post_save 都会 .delay() 投递统计任务，单测环境没有 broker，
    # kombu 建连会无限重试把整轮测试挂死，因此所有写库都收在这里并静默信号。
    @factory.django.mute_signals(signals.post_save)
    def create_task(
        self,
        root_id,
        started_ago=7200,
        is_finished=False,
        is_revoked=False,
        is_expired=False,
        is_deleted=False,
        engine_ver=2,
    ):
        from pipeline.models import PipelineInstance

        from gcloud.core.models import Project
        from gcloud.taskflow3.models import TaskFlowInstance

        project = Project.objects.create(name="project_for_{}".format(root_id), creator="tester")
        pipeline_instance = PipelineInstance.objects.create(
            instance_id=root_id,
            name="instance_for_{}".format(root_id),
            creator="tester",
            is_started=True,
            is_finished=is_finished,
            is_revoked=is_revoked,
            is_expired=is_expired,
            start_time=timezone.now() - datetime.timedelta(seconds=started_ago),
        )
        return TaskFlowInstance.objects.create(
            project=project,
            pipeline_instance=pipeline_instance,
            template_id="1",
            engine_ver=engine_ver,
            is_deleted=is_deleted,
        )

    def create_process(self, root_id, dead=False):
        from pipeline.eri.models import Process

        return Process.objects.create(root_pipeline_id=root_id, priority=100, dead=dead)

    def create_open_case(self, root_id, hit_count=1, last_seen_at=None):
        from pipeline.contrib.diagnostics.models import DiagnosticCase

        from gcloud.contrib.admin.diagnostics.supplement import STUCK_TYPE_NO_LIVE_PROCESS

        now = timezone.now()
        return DiagnosticCase.objects.create(
            root_pipeline_id=root_id,
            node_id="",
            stuck_type=STUCK_TYPE_NO_LIVE_PROCESS,
            severity="critical",
            status=DiagnosticCase.STATUS_OPEN,
            first_seen_at=now,
            last_seen_at=last_seen_at or now,
            hit_count=hit_count,
        )

    @property
    def module(self):
        from gcloud.contrib.admin.diagnostics import supplement

        return supplement


@skipUnless(DIAGNOSTICS_AVAILABLE, "pipeline.contrib.diagnostics unavailable (requires bamboo-pipeline>=3.24.12)")
class SupplementScanRealDataTest(DiagnosticsDataMixin, TestCase):
    """补充检测的判据与误判防线，全部走真实 ORM。"""

    def scan(self, **kwargs):
        return self.module.scan_running_tasks_without_live_process(**kwargs)

    def open_case_roots(self):
        from pipeline.contrib.diagnostics.models import DiagnosticCase

        return set(
            DiagnosticCase.objects.filter(status=DiagnosticCase.STATUS_OPEN).values_list("root_pipeline_id", flat=True)
        )

    def test_long_running_task_without_live_process_is_flagged(self):
        self.create_task("root-stuck", started_ago=7200)

        self.assertEqual(len(self.scan()), 1)
        self.assertEqual(self.open_case_roots(), {"root-stuck"})

    def test_short_lived_task_is_not_flagged(self):
        """扫描期间正常收尾的短命任务：连候选都不该进。"""
        self.create_task("root-young", started_ago=60)

        self.assertEqual(self.scan(), [])
        self.assertEqual(self.open_case_roots(), set())

    def test_task_finished_during_scan_is_not_flagged(self):
        """竞态复现：候选取完之后任务跑完（引擎先写 is_finished 再置进程 dead），立案前二次确认拦住。"""
        from pipeline.models import PipelineInstance

        self.create_task("root-race", started_ago=7200)

        def finish_during_process_query(root_ids):
            PipelineInstance.objects.filter(instance_id="root-race").update(is_finished=True)
            return set()

        with mock.patch(_SUPP + "._roots_with_live_process", side_effect=finish_during_process_query):
            cases = self.scan()

        self.assertEqual(cases, [])
        self.assertEqual(self.open_case_roots(), set())

    def test_task_with_live_process_is_not_flagged(self):
        self.create_task("root-live", started_ago=7200)
        self.create_process("root-live", dead=False)

        self.assertEqual(self.scan(), [])
        self.assertEqual(self.open_case_roots(), set())

    def test_dead_process_does_not_count_as_live(self):
        self.create_task("root-dead-proc", started_ago=7200)
        self.create_process("root-dead-proc", dead=True)

        self.assertEqual(len(self.scan()), 1)

    def test_v1_task_is_not_flagged(self):
        """v1 引擎不用 eri_process，没有存活进程属正常。"""
        self.create_task("root-v1", started_ago=7200, engine_ver=1)

        self.assertEqual(self.scan(), [])

    def test_expired_task_is_not_flagged(self):
        """运行时数据被定期清理的任务本来就没有进程。"""
        self.create_task("root-expired", started_ago=7200, is_expired=True)

        self.assertEqual(self.scan(), [])

    def test_deleted_task_is_not_flagged(self):
        self.create_task("root-deleted", started_ago=7200, is_deleted=True)

        self.assertEqual(self.scan(), [])

    def test_revoked_task_is_not_flagged(self):
        self.create_task("root-revoked", started_ago=7200, is_revoked=True)

        self.assertEqual(self.scan(), [])

    def test_live_process_check_is_batched(self):
        """整批候选只查一次存活进程，判定窗口不随候选数放大。"""
        for index in range(3):
            self.create_task("root-batch-{}".format(index), started_ago=7200)

        with mock.patch(_SUPP + "._roots_with_live_process", return_value=set()) as m_live:
            self.scan()

        self.assertEqual(m_live.call_count, 1)
        self.assertEqual(set(m_live.call_args[0][0]), {"root-batch-0", "root-batch-1", "root-batch-2"})

    def test_batch_limits_candidates(self):
        for index in range(3):
            self.create_task("root-limit-{}".format(index), started_ago=7200)

        self.assertEqual(len(self.scan(batch=2)), 2)

    def test_min_running_seconds_is_configurable(self):
        self.create_task("root-tunable", started_ago=120)

        self.assertEqual(self.scan(min_running_seconds=300), [])
        self.assertEqual(len(self.scan(min_running_seconds=60)), 1)

    def test_task_older_than_window_is_not_flagged(self):
        """跑了一年多、引擎侧数据早已不存在的历史僵尸：治不了也关不掉，不该占取样批次。"""
        self.create_task("root-ancient", started_ago=480 * 24 * 3600)

        self.assertEqual(self.scan(), [])
        self.assertEqual(self.open_case_roots(), set())

    def test_max_running_seconds_is_configurable(self):
        self.create_task("root-window", started_ago=3 * 24 * 3600)

        self.assertEqual(self.scan(max_running_seconds=24 * 3600), [])
        self.assertEqual(len(self.scan(max_running_seconds=7 * 24 * 3600)), 1)


@skipUnless(DIAGNOSTICS_AVAILABLE, "pipeline.contrib.diagnostics unavailable (requires bamboo-pipeline>=3.24.12)")
class CloseRecoveredCasesTest(DiagnosticsDataMixin, TestCase):
    """案例收敛：任务跑完/恢复/消失后，看板上的案例要自动关掉。"""

    def case_status(self, root_id):
        from pipeline.contrib.diagnostics.models import DiagnosticCase

        return list(DiagnosticCase.objects.filter(root_pipeline_id=root_id).values_list("status", flat=True))

    def test_finished_task_case_is_closed(self):
        self.create_task("root-finished", is_finished=True)
        self.create_open_case("root-finished")

        self.assertEqual(self.module.close_recovered_cases(), (1, 0))
        self.assertEqual(self.case_status("root-finished"), ["resolved"])

    def test_still_stuck_case_stays_open(self):
        self.create_task("root-still-stuck")
        self.create_open_case("root-still-stuck")

        self.assertEqual(self.module.close_recovered_cases(), (0, 0))
        self.assertEqual(self.case_status("root-still-stuck"), ["open"])

    def test_recovered_process_closes_case(self):
        self.create_task("root-recovered")
        self.create_process("root-recovered", dead=False)
        self.create_open_case("root-recovered")

        self.assertEqual(self.module.close_recovered_cases(), (1, 0))
        self.assertEqual(self.case_status("root-recovered"), ["resolved"])

    def test_case_without_task_is_closed(self):
        self.create_open_case("root-orphan")

        self.assertEqual(self.module.close_recovered_cases(), (1, 0))
        self.assertEqual(self.case_status("root-orphan"), ["resolved"])

    def test_case_out_of_window_is_ignored(self):
        """任务确实还卡着，但已经超出治理窗口：治不了了，收敛成 ignored 而不是 resolved。"""
        self.create_task("root-aged-out", started_ago=480 * 24 * 3600)
        self.create_open_case("root-aged-out")

        self.assertEqual(self.module.close_recovered_cases(), (0, 1))
        self.assertEqual(self.case_status("root-aged-out"), ["ignored"])

    def test_window_boundary_keeps_case_open(self):
        self.create_task("root-in-window", started_ago=3 * 24 * 3600)
        self.create_open_case("root-in-window")

        self.assertEqual(self.module.close_recovered_cases(max_running_seconds=7 * 24 * 3600), (0, 0))
        self.assertEqual(self.module.close_recovered_cases(max_running_seconds=24 * 3600), (0, 1))

    def test_recurrence_merges_into_existing_resolved_case(self):
        """(root, node, type, status) 唯一，已有 resolved 同键记录时把命中并进去。"""
        from pipeline.contrib.diagnostics.models import DiagnosticCase

        self.create_task("root-merge", is_finished=True)
        resolved = self.create_open_case("root-merge", hit_count=2)
        DiagnosticCase.objects.filter(id=resolved.id).update(status=DiagnosticCase.STATUS_RESOLVED)
        self.create_open_case("root-merge", hit_count=3)

        self.assertEqual(self.module.close_recovered_cases(), (1, 0))
        self.assertEqual(self.case_status("root-merge"), ["resolved"])
        self.assertEqual(DiagnosticCase.objects.get(id=resolved.id).hit_count, 5)

    def test_close_batch_limits_scope(self):
        self.create_task("root-b1", is_finished=True)
        self.create_task("root-b2", is_finished=True)
        self.create_open_case("root-b1", last_seen_at=timezone.now() - datetime.timedelta(hours=2))
        self.create_open_case("root-b2")

        self.assertEqual(self.module.close_recovered_cases(batch=1), (1, 0))
        self.assertEqual(self.case_status("root-b1"), ["resolved"])
        self.assertEqual(self.case_status("root-b2"), ["open"])

    def test_sweep_pages_through_all_open_cases(self):
        for index in range(3):
            self.create_task("root-sweep-{}".format(index), is_finished=True)
            self.create_open_case("root-sweep-{}".format(index))

        self.assertEqual(self.module.sweep_recovered_cases(chunk=1), (3, 3, 0))

    def test_sweep_dry_run_reports_without_writing(self):
        self.create_task("root-dry", is_finished=True)
        self.create_open_case("root-dry")

        self.assertEqual(self.module.sweep_recovered_cases(dry_run=True), (1, 1, 0))
        self.assertEqual(self.case_status("root-dry"), ["open"])

    def test_sweep_reports_aged_out_separately(self):
        self.create_task("root-sweep-aged", started_ago=480 * 24 * 3600)
        self.create_open_case("root-sweep-aged")

        self.assertEqual(self.module.sweep_recovered_cases(), (1, 0, 1))
        self.assertEqual(self.case_status("root-sweep-aged"), ["ignored"])

    def test_command_reports_closed_count(self):
        from io import StringIO

        from django.core.management import call_command

        self.create_task("root-cmd", is_finished=True)
        self.create_open_case("root-cmd")

        out = StringIO()
        call_command("close_recovered_diagnostic_cases", stdout=out)

        self.assertIn("scanned=1 resolved=1 ignored=0", out.getvalue())
        self.assertEqual(self.case_status("root-cmd"), ["resolved"])

    def test_command_dry_run_marks_output(self):
        from io import StringIO

        from django.core.management import call_command

        self.create_task("root-cmd-dry", is_finished=True)
        self.create_open_case("root-cmd-dry")

        out = StringIO()
        call_command("close_recovered_diagnostic_cases", "--dry-run", stdout=out)

        self.assertIn("would_resolved=1", out.getvalue())
        self.assertEqual(self.case_status("root-cmd-dry"), ["open"])
