# -*- coding: utf-8 -*-
"""Exercise consolidated controls against the pinned runtime and real records."""
import json
from contextlib import contextmanager
from datetime import timedelta
from unittest import mock

from bamboo_engine.config import Settings as BambooSettings
from bamboo_engine.fence import FENCE_HEADER
from django.test import TestCase, override_settings
from django.utils import timezone
from fakeredis import FakeRedis
from pipeline.contrib.diagnostics import events, metrics
from pipeline.contrib.diagnostics.models import DiagnosticCase, DiagnosticEvent, DiagnosticRecovery
from pipeline.contrib.diagnostics.recovery import dispatch, plan_replay, replay_case
from pipeline.eri.models import Node, Process, State, SyncAdvanceCheckpoint
from pipeline.eri.runtime import BambooDjangoRuntime

from gcloud.contrib.admin import tasks
from gcloud.tests.contrib.admin.diagnostics.test_supplement import DiagnosticsDataMixin
from gcloud.tests.contrib.admin.diagnostics.test_switch_config import load_switch_settings


@contextmanager
def configured(**environ):
    resolved = load_switch_settings(environ)
    django_settings = {name: value for name, value in resolved.items() if name.isupper()}
    with override_settings(redis_inst=FakeRedis(), **django_settings), mock.patch.multiple(
        BambooSettings, **vars(resolved["BambooSettings"])
    ):
        yield


class S7SwitchRuntimeTest(DiagnosticsDataMixin, TestCase):
    def setUp(self):
        self.root = "s7-switch-root"
        self.task = self.create_task(self.root)
        self.process = Process.objects.create(
            root_pipeline_id=self.root,
            current_node_id="a",
            priority=1,
            asleep=False,
            pipeline_stack=json.dumps([self.root]),
        )
        now = timezone.now()
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
        self.runtime = BambooDjangoRuntime()
        self.environ = {
            "BKAPP_DIAGNOSTICS_DETECTION_ENABLED": "1",
            "BKAPP_DIAGNOSTICS_SCANNERS": "signature",
            "BKAPP_DIAGNOSTICS_SECOND_CONFIRM_SECONDS": "0",
            "BKAPP_DIAGNOSTICS_S7_ENABLED": "1",
            "BKAPP_PIPELINE_FENCE_MODE": "enforce",
        }

    def prepare_checkpoint(self):
        self.assertTrue(self.runtime.prepare_sync_advance(self.process.pk, "a", "v1", "a-next"))
        ago = timezone.now() - timedelta(seconds=500)
        SyncAdvanceCheckpoint.objects.filter(process_id=self.process.pk).update(prepared_at=ago)
        Process.objects.filter(pk=self.process.pk).update(last_heartbeat=ago)

    def prepare_and_detect(self):
        self.prepare_checkpoint()
        tasks.scan_stuck_signatures()
        return DiagnosticCase.objects.get(stuck_type="sync_advance_stalled", root_pipeline_id=self.root)

    def assert_checkpoint_ready(self):
        self.assertEqual(SyncAdvanceCheckpoint.objects.get(process_id=self.process.pk).phase, "READY")
        self.assertFalse(Process.objects.get(pk=self.process.pk).asleep)

    def test_s7_enables_detection_and_real_checkpoint_takeover(self):
        self.environ.update(
            BKAPP_DIAGNOSTICS_RECOVERY_POLICY="auto",
            BKAPP_DIAGNOSTICS_RECOVERY_PROJECT_IDS=str(self.task.project_id),
            BKAPP_DIAGNOSTICS_AUTO_REPLAY_TYPES="sync_advance_stalled",
        )
        with configured(**self.environ), mock.patch.object(BambooDjangoRuntime, "execute") as send:
            case = self.prepare_and_detect()
            tasks.run_stuck_recovery()
            tasks.run_stuck_recovery()
        send.assert_called_once()
        self.assertEqual(send.call_args[1]["headers"], {FENCE_HEADER: {"from_node": "a", "from_version": "v1"}})
        self.assertEqual(send.call_args[1]["node_id"], "a-next")
        self.assertEqual(SyncAdvanceCheckpoint.objects.get(process_id=self.process.pk).phase, "RELEASED")
        self.assertTrue(Process.objects.get(pk=self.process.pk).asleep)
        self.assertEqual(DiagnosticRecovery.objects.get(case=case).status, "dispatched")

    def test_s7_off_rejects_previously_built_plan_without_changing_checkpoint(self):
        with configured(**self.environ):
            plan = plan_replay(self.prepare_and_detect())
            self.assertEqual(plan.blockers, [])
        self.environ["BKAPP_DIAGNOSTICS_S7_ENABLED"] = "0"
        with configured(**self.environ), mock.patch.object(BambooDjangoRuntime, "execute") as send:
            with self.assertRaisesRegex(ValueError, "sync advance recovery switches are off"):
                dispatch(plan.message)
        send.assert_not_called()
        self.assert_checkpoint_ready()

    def test_s7_alone_does_not_enable_automatic_or_manual_recovery(self):
        with configured(**self.environ), mock.patch.object(BambooDjangoRuntime, "execute") as send:
            case = self.prepare_and_detect()
            tasks.run_stuck_recovery()
            self.assertFalse(DiagnosticRecovery.objects.exists())
            result = replay_case(case.pk, operator="tester", mode="apply")
        self.assertIn("apply disabled", result.blockers)
        send.assert_not_called()
        self.assert_checkpoint_ready()

    def test_s7_off_excludes_awake_sync_process_from_detection(self):
        with configured(**self.environ):
            self.prepare_checkpoint()
        self.environ["BKAPP_DIAGNOSTICS_S7_ENABLED"] = "0"
        with configured(**self.environ):
            tasks.scan_stuck_signatures()
        self.assertFalse(DiagnosticCase.objects.exists())
        self.assert_checkpoint_ready()

    def test_s7_still_requires_fence_enforcement(self):
        self.environ.update(BKAPP_PIPELINE_FENCE_MODE="observe", BKAPP_DIAGNOSTICS_MANUAL_APPLY_ENABLED="1")
        with configured(**self.environ), mock.patch.object(BambooDjangoRuntime, "execute") as send:
            case = self.prepare_and_detect()
            result = replay_case(case.pk, operator="tester", mode="apply", confirm_risk=True)
        self.assertFalse(result.result)
        self.assertIn("sync advance checkpoint and both fence switches must be enabled", result.blockers)
        send.assert_not_called()
        self.assert_checkpoint_ready()


class ObservabilitySwitchRuntimeTest(TestCase):
    def emit(self):
        event = events.emit_event(event_type="stuck", root_pipeline_id="observe-root")
        metrics.emit_alert_log("stuck", "observe-root")
        return event

    def test_defaults_and_off_have_no_event_database_access_or_alert_logs(self):
        for environ in ({}, {"BKAPP_DIAGNOSTICS_OBSERVABILITY_MODE": "off"}):
            with self.subTest(environ=environ), configured(**environ), mock.patch.object(metrics, "logger") as logger:
                with self.assertNumQueries(0):
                    self.assertIsNone(self.emit())
                logger.warning.assert_not_called()

    def test_alerts_only_has_no_event_database_access(self):
        with configured(BKAPP_DIAGNOSTICS_OBSERVABILITY_MODE="alerts"), self.assertLogs(metrics.logger.name) as logs:
            with self.assertNumQueries(0):
                self.assertIsNone(self.emit())
        self.assertIn("[pipeline_diagnostics_alert]", logs.output[0])

    def test_full_records_event_and_emits_alert(self):
        with configured(BKAPP_DIAGNOSTICS_OBSERVABILITY_MODE="full"), mock.patch.object(
            events, "_EVENT_TABLE_AVAILABLE", None
        ), self.assertLogs(metrics.logger.name) as logs:
            event = self.emit()
        self.assertEqual(DiagnosticEvent.objects.get(pk=event.pk).root_pipeline_id, "observe-root")
        self.assertIn("[pipeline_diagnostics_alert]", logs.output[0])

    def test_legacy_event_only_configuration_keeps_alerts_disabled(self):
        with configured(BKAPP_DIAGNOSTICS_EVENT_ENABLED="1", BKAPP_DIAGNOSTICS_ALERT_ENABLED="0"), mock.patch.object(
            events, "_EVENT_TABLE_AVAILABLE", None
        ), mock.patch.object(metrics, "logger") as logger:
            event = self.emit()
        self.assertTrue(DiagnosticEvent.objects.filter(pk=event.pk).exists())
        logger.warning.assert_not_called()
