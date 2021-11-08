# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from django.db import models
from django.utils.translation import ugettext_lazy as _


class DjCrontabSchedule(models.Model):
    minute = models.CharField(max_length=64, default="*")
    hour = models.CharField(max_length=64, default="*")
    day_of_week = models.CharField(max_length=64, default="*")
    day_of_month = models.CharField(max_length=64, default="*")
    month_of_year = models.CharField(max_length=64, default="*")

    class Meta:
        db_table = "djcelery_crontabschedule"


class DjPeriodicTasks(models.Model):
    ident = models.SmallIntegerField(default=1, primary_key=True, unique=True)
    last_update = models.DateTimeField(null=False)

    class Meta:
        db_table = "djcelery_periodictasks"


class DjIntervalSchedule(models.Model):
    every = models.IntegerField(_("every"), null=False)
    period = models.CharField(_("period"), max_length=24)

    class Meta:
        db_table = "djcelery_intervalschedule"
        verbose_name = _("interval")
        verbose_name_plural = _("intervals")
        ordering = ["period", "every"]


class DjPeriodicTask(models.Model):
    name = models.CharField(_("name"), max_length=200, unique=True, help_text=_("Useful description"), )
    task = models.CharField(_("task name"), max_length=200)
    interval = models.ForeignKey(
        DjIntervalSchedule,
        null=True,
        blank=True,
        verbose_name=_("interval"),
        on_delete=models.CASCADE,
    )
    crontab = models.ForeignKey(
        DjCrontabSchedule,
        null=True,
        blank=True,
        verbose_name=_("crontab"),
        on_delete=models.CASCADE,
        help_text=_("Use one of interval/crontab"),
    )
    args = models.TextField(
        _("Arguments"),
        blank=True,
        default="[]",
        help_text=_("JSON encoded positional arguments"),
    )
    kwargs = models.TextField(
        _("Keyword arguments"),
        blank=True,
        default="{}",
        help_text=_("JSON encoded keyword arguments"),
    )
    queue = models.CharField(
        _("queue"),
        max_length=200,
        blank=True,
        null=True,
        default=None,
        help_text=_("Queue defined in CELERY_QUEUES"),
    )
    exchange = models.CharField(_("exchange"), max_length=200, blank=True, null=True, default=None, )
    routing_key = models.CharField(_("routing key"), max_length=200, blank=True, null=True, default=None, )
    expires = models.DateTimeField(_("expires"), blank=True, null=True)
    enabled = models.BooleanField(_("enabled"), default=True)
    last_run_at = models.DateTimeField(
        auto_now=False,
        auto_now_add=False,
        editable=False,
        blank=True,
        null=True,
    )
    total_run_count = models.PositiveIntegerField(default=0, editable=False)
    date_changed = models.DateTimeField(auto_now=True)
    description = models.TextField(_("description"), blank=True)

    no_changes = False

    class Meta:
        db_table = "djcelery_periodictask"
        verbose_name = _("periodic task")
        verbose_name_plural = _("periodic tasks")


class DjWorkerState(models.Model):
    hostname = models.CharField(_("hostname"), max_length=255, unique=True)
    last_heartbeat = models.DateTimeField(_("last heartbeat"), null=True, db_index=True)

    class Meta:
        """Model meta-data."""

        verbose_name = _("worker")
        verbose_name_plural = _("workers")
        get_latest_by = "last_heartbeat"
        ordering = ["-last_heartbeat"]


class DjTaskState(models.Model):
    state = models.CharField(_("state"), max_length=64)
    task_id = models.CharField(_("UUID"), max_length=36, unique=True)
    name = models.CharField(_("name"), max_length=200, null=True, db_index=True)
    tstamp = models.DateTimeField(_("event received at"), db_index=True)
    args = models.TextField(_("Arguments"), null=True)
    kwargs = models.TextField(_("Keyword arguments"), null=True)
    eta = models.DateTimeField(_("ETA"), null=True)
    expires = models.DateTimeField(_("expires"), null=True)
    result = models.TextField(_("result"), null=True)
    traceback = models.TextField(_("traceback"), null=True)
    runtime = models.FloatField(
        _("execution time"),
        null=True,
        help_text=_("in seconds if task succeeded"),
    )
    retries = models.IntegerField(_("number of retries"), default=0)
    worker = models.ForeignKey(
        DjWorkerState,
        null=True,
        verbose_name=_("worker"),
        on_delete=models.CASCADE,
    )
    hidden = models.BooleanField(editable=False, default=False, db_index=True)

    class Meta:
        """Model meta-data."""

        verbose_name = _("task")
        verbose_name_plural = _("tasks")
        get_latest_by = "tstamp"
        ordering = ["-tstamp"]


def execute(new_table, old_table, tz=None):  # pylint: disable=invalid-name
    for old_data in old_table.objects.all():
        new_data = new_table()
        if tz:
            new_data.__setattr__("timezone", tz)
        for field in old_data._meta.fields:
            field_name = field.name
            # 判断是否为外键
            if field_name in ("crontab", "interval", "worker"):
                try:
                    # 写入外键id
                    new_data.__setattr__(
                        field_name + "_id", old_data.__getattribute__(field_name).id
                    )
                except AttributeError:
                    new_data.__setattr__(field_name + "_id", None)
            else:
                new_data.__setattr__(field_name, old_data.__getattribute__(field_name))
        new_data.save()
