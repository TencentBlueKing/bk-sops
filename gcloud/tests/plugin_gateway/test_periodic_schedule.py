# -*- coding: utf-8 -*-
from datetime import timedelta
from unittest.mock import patch

from celery import Celery
from django.conf import settings
from django.test import TestCase
from django.utils import timezone
from django_celery_beat.models import IntervalSchedule, PeriodicTask
from django_celery_beat.schedulers import DatabaseScheduler


class PluginGatewaySweepScheduleTestCase(TestCase):
    schedule_name = "sweep_expired_plugin_gateway_runs"

    def setUp(self):
        self.app = Celery("plugin_gateway_schedule_test", broker="memory://", set_as_current=False)
        self.app.conf.update(result_expires=None, timezone=settings.TIME_ZONE)
        self.addCleanup(self.app.close)
        self.entry = dict(settings.CELERYBEAT_SCHEDULE[self.schedule_name])
        self.interval = IntervalSchedule.objects.create(every=60, period=IntervalSchedule.SECONDS)

    def start_scheduler(self, enabled):
        self.app.conf.beat_schedule = {self.schedule_name: dict(self.entry, enabled=enabled)}
        scheduler = DatabaseScheduler(app=self.app)
        self.addCleanup(scheduler.close)
        return scheduler

    def create_sweep(self, enabled):
        return PeriodicTask.objects.create(
            name=self.schedule_name,
            task=self.entry["task"],
            interval=self.interval,
            enabled=enabled,
            last_run_at=timezone.now() - timedelta(minutes=2),
        )

    def test_disabled_fresh_schedule_does_not_publish(self):
        scheduler = self.start_scheduler(enabled=False)

        self.assertFalse(PeriodicTask.objects.get(name=self.schedule_name).enabled)
        self.assertNotIn(self.schedule_name, scheduler.schedule)
        with patch.object(scheduler, "apply_async") as publish:
            scheduler.tick()
        publish.assert_not_called()

    def test_disabled_existing_schedule_preserves_other_periodic_tasks(self):
        sweep = self.create_sweep(enabled=True)
        other = PeriodicTask.objects.create(
            name="unrelated_periodic_task",
            task="tests.unrelated_periodic_task",
            interval=self.interval,
            last_run_at=timezone.now() - timedelta(minutes=2),
        )

        scheduler = self.start_scheduler(enabled=False)

        sweep.refresh_from_db()
        other.refresh_from_db()
        self.assertFalse(sweep.enabled)
        self.assertTrue(other.enabled)
        self.assertNotIn(self.schedule_name, scheduler.schedule)
        self.assertIn(other.name, scheduler.schedule)
        with patch.object(scheduler, "apply_async") as publish:
            scheduler.tick()
        self.assertEqual(publish.call_count, 1)
        self.assertEqual(publish.call_args[0][0].task, other.task)

    def test_enabled_schedule_reuses_and_resumes_existing_record(self):
        sweep = self.create_sweep(enabled=False)

        scheduler = self.start_scheduler(enabled=True)

        sweep.refresh_from_db()
        self.assertTrue(sweep.enabled)
        self.assertEqual(PeriodicTask.objects.get(name=self.schedule_name).pk, sweep.pk)
        self.assertIn(self.schedule_name, scheduler.schedule)
        # 停用记录会清空 last_run_at，重新启用后需等到下一个扫描周期。
        with patch("django_celery_beat.models.now", return_value=timezone.now() + timedelta(minutes=2)):
            with patch.object(scheduler, "apply_async") as publish:
                scheduler.tick()
        self.assertEqual(publish.call_count, 1)
        self.assertEqual(publish.call_args[0][0].task, self.entry["task"])
        self.assertEqual(publish.call_args[0][0].options["queue"], "open_plugin_polling")
