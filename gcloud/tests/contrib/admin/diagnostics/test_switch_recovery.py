# -*- coding: utf-8 -*-
"""Exercise unified settings through the scheduled task and real recovery records."""
import json
from contextlib import contextmanager
from datetime import timedelta
from types import SimpleNamespace
from unittest import mock

from bamboo_engine.config import Settings as BambooSettings
from bamboo_engine.fence import FENCE_HEADER
from django.test import TestCase, override_settings
from django.utils import timezone
from fakeredis import FakeRedis
from pipeline.contrib.diagnostics.models import DiagnosticCase, DiagnosticRecovery
from pipeline.contrib.diagnostics.recovery import BLOCKER_APPLY_DISABLED, BLOCKER_ENFORCE_OFF, replay_case
from pipeline.eri.models import Node, Process, State

from gcloud.contrib.admin import tasks
from gcloud.tests.contrib.admin.diagnostics.test_supplement import DiagnosticsDataMixin
from gcloud.tests.contrib.admin.diagnostics.test_switch_config import load_switch_settings


class SwitchRecoveryIntegrationTest(DiagnosticsDataMixin, TestCase):
    def setUp(self):
        self.root = "switch-recovery-root"
        self.task = self.create_task(self.root)
        self.process = Process.objects.create(
            root_pipeline_id=self.root, current_node_id="a", priority=1, asleep=True, pipeline_stack="[]"
        )
        now = timezone.now()
        Process.objects.filter(pk=self.process.pk).update(last_heartbeat=now - timedelta(seconds=900))
        Node.objects.create(node_id="a", detail=json.dumps({"type": "ServiceActivity", "targets": {"f": "a-next"}}))
        State.objects.create(node_id=self.root, root_id=self.root, name="RUNNING", version="root-v")
        State.objects.create(
            node_id="a",
            root_id=self.root,
            name="FINISHED",
            version="v1",
            started_time=now - timedelta(seconds=900),
            archived_time=now - timedelta(seconds=600),
        )
        self.case = DiagnosticCase.objects.create(
            root_pipeline_id=self.root,
            node_id="a",
            stuck_type="execute_dispatch_lost",
            related_objects={"process_id": self.process.pk},
            evidence={"state_version": "v1"},
        )
        patcher = mock.patch("pipeline.contrib.diagnostics.recovery._runtime")
        self.runtime = patcher.start().return_value
        self.addCleanup(patcher.stop)
        self.runtime.get_process_info.return_value = SimpleNamespace(
            root_pipeline_id=self.root, top_pipeline_id=self.root
        )
        self.redis = FakeRedis()

    @contextmanager
    def configured(self, policy="auto", **overrides):
        environ = {
            "BKAPP_DIAGNOSTICS_DETECTION_ENABLED": "0",
            "BKAPP_PIPELINE_FENCE_MODE": "enforce",
            "BKAPP_DIAGNOSTICS_AUTO_REPLAY_TYPES": "execute_dispatch_lost",
            "BKAPP_DIAGNOSTICS_RECOVERY_PROJECT_IDS": str(self.task.project_id),
        }
        if policy is not None:
            environ["BKAPP_DIAGNOSTICS_RECOVERY_POLICY"] = policy
        environ.update(overrides)
        resolved = load_switch_settings(environ)
        django_settings = {name: value for name, value in resolved.items() if name.isupper()}
        with override_settings(redis_inst=self.redis, **django_settings), mock.patch.multiple(
            BambooSettings, **vars(resolved["BambooSettings"])
        ):
            yield

    def dispatch_due_record(self):
        with self.configured():
            tasks.run_stuck_recovery()
        row = DiagnosticRecovery.objects.get(case=self.case)
        self.assertEqual(row.status, DiagnosticRecovery.STATUS_DISPATCHED)
        DiagnosticRecovery.objects.filter(pk=row.pk).update(created_at=timezone.now() - timedelta(seconds=600))
        self.runtime.reset_mock()
        return row

    def test_auto_dispatches_only_once_with_fence_but_does_not_enable_manual_apply(self):
        with self.configured():
            tasks.run_stuck_recovery()
            tasks.run_stuck_recovery()
            result = replay_case(self.case.pk, operator="tester", mode="apply")
        self.assertIn(BLOCKER_APPLY_DISABLED, result.blockers)
        self.runtime.execute.assert_called_once_with(
            process_id=self.process.pk,
            node_id="a-next",
            root_pipeline_id=self.root,
            parent_pipeline_id=self.root,
            headers={FENCE_HEADER: {"from_node": "a", "from_version": "v1"}},
        )
        row = DiagnosticRecovery.objects.get(case=self.case)
        self.assertEqual((row.trigger, row.mode, row.status), ("auto", "apply", "dispatched"))

    def test_preview_records_plan_without_dispatch(self):
        with self.configured(policy="preview"):
            tasks.run_stuck_recovery()
            tasks.run_stuck_recovery()
        self.runtime.execute.assert_not_called()
        row = DiagnosticRecovery.objects.get(case=self.case)
        self.assertEqual((row.mode, row.status), ("preview", "previewed"))
        self.assertEqual(row.message["node_id"], "a-next")

    def test_manual_alias_allows_manual_replay_while_automatic_recovery_is_off(self):
        with self.configured(policy="off", BKAPP_DIAGNOSTICS_MANUAL_APPLY_ENABLED="1"):
            tasks.run_stuck_recovery()
            self.assertEqual(DiagnosticRecovery.objects.count(), 0)
            result = replay_case(self.case.pk, operator="tester", mode="apply")
        self.assertTrue(result.result)
        self.runtime.execute.assert_called_once()
        row = DiagnosticRecovery.objects.get(case=self.case)
        self.assertEqual((row.trigger, row.mode, row.status), ("manual", "apply", "dispatched"))

    def test_manual_alias_off_does_not_disable_automatic_recovery(self):
        with self.configured(BKAPP_DIAGNOSTICS_MANUAL_APPLY_ENABLED="0"):
            result = replay_case(self.case.pk, operator="tester", mode="apply")
            self.assertIn(BLOCKER_APPLY_DISABLED, result.blockers)
            self.runtime.execute.assert_not_called()
            tasks.run_stuck_recovery()
        self.runtime.execute.assert_called_once()
        row = DiagnosticRecovery.objects.get(case=self.case)
        self.assertEqual((row.trigger, row.mode, row.status), ("auto", "apply", "dispatched"))

    def test_auto_preserves_project_and_type_restrictions(self):
        for overrides in (
            {"BKAPP_DIAGNOSTICS_RECOVERY_PROJECT_IDS": ""},
            {"BKAPP_DIAGNOSTICS_RECOVERY_PROJECT_IDS": str(self.task.project_id + 1)},
            {"BKAPP_DIAGNOSTICS_AUTO_REPLAY_TYPES": ""},
            {"BKAPP_DIAGNOSTICS_AUTO_REPLAY_TYPES": "callback_dispatch_lost"},
        ):
            with self.subTest(overrides=overrides), self.configured(**overrides):
                tasks.run_stuck_recovery()
                row = DiagnosticRecovery.objects.get(case=self.case)
                self.assertEqual((row.mode, row.status), ("preview", "previewed"))
                self.runtime.execute.assert_not_called()
                DiagnosticRecovery.objects.all().delete()

    def test_observe_blocks_execute_recovery(self):
        with self.configured(BKAPP_PIPELINE_FENCE_MODE="observe"):
            tasks.run_stuck_recovery()
        self.runtime.execute.assert_not_called()
        row = DiagnosticRecovery.objects.get(case=self.case)
        self.assertEqual(row.status, DiagnosticRecovery.STATUS_BLOCKED)
        self.assertIn(BLOCKER_ENFORCE_OFF, row.detail["blockers"])

    def test_off_settles_still_stuck_record_without_new_plan_or_retry(self):
        row = self.dispatch_due_record()
        with self.configured(policy="off"):
            tasks.run_stuck_recovery()
            tasks.run_stuck_recovery()
        row.refresh_from_db()
        self.assertEqual(row.status, DiagnosticRecovery.STATUS_INEFFECTIVE)
        self.assertIsNotNone(row.settled_at)
        self.assertTrue(row.detail["settled_holds"])
        self.assertEqual(DiagnosticRecovery.objects.count(), 1)
        self.runtime.execute.assert_not_called()
        self.runtime.schedule.assert_not_called()

    def test_off_settles_progressed_record_as_applied(self):
        row = self.dispatch_due_record()
        Process.objects.filter(pk=self.process.pk).update(current_node_id="a-next", asleep=False)
        with self.configured(policy="off"):
            tasks.run_stuck_recovery()
        row.refresh_from_db()
        self.assertEqual(row.status, DiagnosticRecovery.STATUS_APPLIED)
        self.assertIsNotNone(row.settled_at)
        self.runtime.execute.assert_not_called()

    def test_legacy_disabled_remains_noop_even_with_pending_records(self):
        row = self.dispatch_due_record()
        with self.configured(policy=None, BKAPP_DIAGNOSTICS_RECOVERY_ENABLED="0"):
            with self.assertNumQueries(0):
                tasks.run_stuck_recovery()
        row.refresh_from_db()
        self.assertEqual(row.status, DiagnosticRecovery.STATUS_DISPATCHED)
        self.assertIsNone(row.settled_at)
        self.runtime.execute.assert_not_called()
