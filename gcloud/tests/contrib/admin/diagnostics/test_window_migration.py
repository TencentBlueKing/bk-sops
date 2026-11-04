# -*- coding: utf-8 -*-
"""Check window coverage, backfill and rollback against the pinned runtime."""
from contextlib import contextmanager
from datetime import timedelta
from io import StringIO

from django.core.management import call_command
from django.test import TestCase, override_settings
from django.utils import timezone
from fakeredis import FakeRedis
from pipeline.contrib.diagnostics.models import DiagnosticCase, DiagnosticScanCursor
from pipeline.eri.models import Process, State

from gcloud.contrib.admin import tasks
from gcloud.tests.contrib.admin.diagnostics.test_supplement import DiagnosticsDataMixin
from gcloud.tests.contrib.admin.diagnostics.test_switch_config import load_switch_settings


class WindowMigrationTest(DiagnosticsDataMixin, TestCase):
    def setUp(self):
        self.redis = FakeRedis()

    def stuck_root(self, root, age):
        self.create_task(root, started_ago=age + 60)
        process = self.create_process(root)
        Process.objects.filter(pk=process.pk).update(
            current_node_id=root + "-node", last_heartbeat=timezone.now() - timedelta(seconds=age), asleep=True
        )
        State.objects.create(node_id=root, root_id=root, name="RUNNING", version="root-v")

    def case_roots(self):
        return set(DiagnosticCase.objects.values_list("root_pipeline_id", flat=True))

    def cursors(self):
        return list(DiagnosticScanCursor.objects.order_by("pk").values())

    @contextmanager
    def configured(self, **environ):
        env = {"BKAPP_DIAGNOSTICS_SECOND_CONFIRM_SECONDS": "0"}
        env.update(environ)
        resolved = load_switch_settings(env)
        django_settings = {name: value for name, value in resolved.items() if name.isupper()}
        with override_settings(redis_inst=self.redis, **django_settings):
            yield

    def test_legacy_scan_flag_uses_windows_and_requires_explicit_history_backfill(self):
        for i in range(3):
            self.stuck_root("recent-{}".format(i), 4000 + i)
        self.stuck_root("history", 2 * 86400)
        self.stuck_root("out-of-range", 8 * 86400)
        with self.configured(
            BKAPP_DIAGNOSTICS_SCAN_ENABLED="1",
            BKAPP_DIAGNOSTICS_WINDOW_SCAN_ENABLED="0",
            BKAPP_DIAGNOSTICS_SCAN_BATCH="1",
        ):
            tasks.scan_stuck_diagnostics()
        self.assertEqual(self.case_roots(), {"recent-0", "recent-1", "recent-2"})
        self.assertEqual(len(self.cursors()), 2)

    @override_settings(PIPELINE_DIAGNOSTICS_SCAN_PAGE_SIZE=1)
    def test_window_cap_pause_resume_and_legacy_window_config_share_cursor(self):
        for i in range(3):
            self.stuck_root("crossing-{}".format(i), 4000 + i)
        with self.configured(
            BKAPP_DIAGNOSTICS_DETECTION_ENABLED="1",
            BKAPP_DIAGNOSTICS_SCANNERS="window",
            BKAPP_DIAGNOSTICS_WINDOW_MAX_ROOTS="1",
        ):
            tasks.scan_stuck_diagnostics()
        self.assertEqual(len(self.case_roots()), 1)
        cursor = self.cursors()
        with self.configured(BKAPP_DIAGNOSTICS_DETECTION_ENABLED="0"):
            with self.assertNumQueries(0):
                tasks.scan_stuck_diagnostics()
        self.assertEqual(self.cursors(), cursor)
        with self.configured(
            BKAPP_DIAGNOSTICS_DETECTION_ENABLED="1",
            BKAPP_DIAGNOSTICS_SCANNERS="window",
            BKAPP_DIAGNOSTICS_WINDOW_MAX_ROOTS="1",
        ):
            tasks.scan_stuck_diagnostics()
        self.assertEqual(len(self.case_roots()), 2)
        # Removing new controls and restoring the old window flag resumes the same progress.
        with self.configured(BKAPP_DIAGNOSTICS_WINDOW_SCAN_ENABLED="1", BKAPP_DIAGNOSTICS_WINDOW_MAX_ROOTS="1"):
            tasks.scan_stuck_diagnostics()
        self.assertEqual(self.case_roots(), {"crossing-0", "crossing-1", "crossing-2"})

    def test_historical_backfill_is_explicit_and_does_not_change_periodic_progress(self):
        self.stuck_root("crossing", 4000)
        self.stuck_root("history", 2 * 86400)
        with self.configured(BKAPP_DIAGNOSTICS_DETECTION_ENABLED="1", BKAPP_DIAGNOSTICS_SCANNERS="window"):
            tasks.scan_stuck_diagnostics()
            self.assertEqual(self.case_roots(), {"crossing"})
            cursor = self.cursors()
            cases = list(DiagnosticCase.objects.order_by("pk").values())
            output = StringIO()
            args = (
                "diagnostics_scan",
                "--scanner",
                "window",
                "--tier",
                "3600",
                "--start-seconds",
                "604800",
                "--confirm",
                "0",
                "--max-rows",
                "2000",
            )
            call_command(*args, dry_run=True, stdout=output)
            self.assertIn("root=history", output.getvalue())
            self.assertEqual(list(DiagnosticCase.objects.order_by("pk").values()), cases)
            self.assertEqual(self.cursors(), cursor)
            call_command(*args, stdout=StringIO())
        self.assertEqual(self.case_roots(), {"crossing", "history"})
        self.assertEqual(self.cursors(), cursor)

    def test_legacy_scan_alias_does_not_reset_windows_or_implicitly_backfill_history(self):
        self.stuck_root("history", 2 * 86400)
        with self.configured(BKAPP_DIAGNOSTICS_DETECTION_ENABLED="1", BKAPP_DIAGNOSTICS_SCANNERS="window"):
            tasks.scan_stuck_diagnostics()
        self.assertEqual(self.case_roots(), set())
        cursor_ids = set(DiagnosticScanCursor.objects.values_list("pk", flat=True))
        with self.configured(BKAPP_DIAGNOSTICS_SCAN_ENABLED="1"):
            tasks.scan_stuck_diagnostics()
        self.assertEqual(self.case_roots(), set())
        self.assertEqual(set(DiagnosticScanCursor.objects.values_list("pk", flat=True)), cursor_ids)
