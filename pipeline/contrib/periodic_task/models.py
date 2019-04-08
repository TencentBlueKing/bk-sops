# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from __future__ import absolute_import

import ujson as json
from datetime import timedelta

import timezone_field
from django.db import models
from django.db.models import signals
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import MultipleObjectsReturned, ValidationError
from celery import schedules

from pipeline.exceptions import InvalidOperationException
from pipeline.models import Snapshot, PipelineTemplate, PipelineInstance, CompressJSONField
from pipeline.utils.uniqid import uniqid
from pipeline.contrib.periodic_task.signals import periodic_task_start_failed
from pipeline.contrib.periodic_task.djcelery.compat import python_2_unicode_compatible
from pipeline.contrib.periodic_task.djcelery.tzcrontab import TzAwareCrontab
from pipeline.contrib.periodic_task.djcelery import managers
from pipeline.contrib.periodic_task.djcelery.utils import now

PERIOD_CHOICES = (('days', _('Days')),
                  ('hours', _('Hours')),
                  ('minutes', _('Minutes')),
                  ('seconds', _('Seconds')),
                  ('microseconds', _('Microseconds')))


@python_2_unicode_compatible
class IntervalSchedule(models.Model):
    every = models.IntegerField(_('every'), null=False)
    period = models.CharField(
        _('period'), max_length=24, choices=PERIOD_CHOICES,
    )

    class Meta:
        verbose_name = _('interval')
        verbose_name_plural = _('intervals')
        ordering = ['period', 'every']

    @property
    def schedule(self):
        return schedules.schedule(timedelta(**{self.period: self.every}))

    @classmethod
    def from_schedule(cls, schedule, period='seconds'):
        every = max(schedule.run_every.total_seconds(), 0)
        try:
            return cls.objects.get(every=every, period=period)
        except cls.DoesNotExist:
            return cls(every=every, period=period)
        except MultipleObjectsReturned:
            cls.objects.filter(every=every, period=period).delete()
            return cls(every=every, period=period)

    def __str__(self):
        if self.every == 1:
            return _('every {0.period_singular}').format(self)
        return _('every {0.every:d} {0.period}').format(self)

    @property
    def period_singular(self):
        return self.period[:-1]


def cronexp(field):
    return field and str(field).replace(' ', '') or '*'


@python_2_unicode_compatible
class CrontabSchedule(models.Model):
    minute = models.CharField(_('minute'), max_length=64, default='*')
    hour = models.CharField(_('hour'), max_length=64, default='*')
    day_of_week = models.CharField(
        _('day of week'), max_length=64, default='*',
    )
    day_of_month = models.CharField(
        _('day of month'), max_length=64, default='*',
    )
    month_of_year = models.CharField(
        _('month of year'), max_length=64, default='*',
    )
    timezone = timezone_field.TimeZoneField(default='UTC')

    class Meta:
        verbose_name = _('crontab')
        verbose_name_plural = _('crontabs')
        ordering = ['month_of_year', 'day_of_month',
                    'day_of_week', 'hour', 'minute']

    def __str__(self):
        return '{0} {1} {2} {3} {4} (m/h/d/dM/MY)'.format(
            cronexp(self.minute),
            cronexp(self.hour),
            cronexp(self.day_of_week),
            cronexp(self.day_of_month),
            cronexp(self.month_of_year),
        )

    @property
    def schedule(self):
        return TzAwareCrontab(
            minute=self.minute,
            hour=self.hour, day_of_week=self.day_of_week,
            day_of_month=self.day_of_month,
            month_of_year=self.month_of_year,
            tz=self.timezone)

    @classmethod
    def from_schedule(cls, schedule):
        spec = {'minute': schedule._orig_minute,
                'hour': schedule._orig_hour,
                'day_of_week': schedule._orig_day_of_week,
                'day_of_month': schedule._orig_day_of_month,
                'month_of_year': schedule._orig_month_of_year,
                'timezone': schedule.tz
                }
        try:
            return cls.objects.get(**spec)
        except cls.DoesNotExist:
            return cls(**spec)
        except MultipleObjectsReturned:
            cls.objects.filter(**spec).delete()
            return cls(**spec)


class DjCeleryPeriodicTasks(models.Model):
    ident = models.SmallIntegerField(default=1, primary_key=True, unique=True)
    last_update = models.DateTimeField(null=False)

    objects = managers.ExtendedManager()

    @classmethod
    def changed(cls, instance, **kwargs):
        if not instance.no_changes:
            cls.objects.update_or_create(ident=1,
                                         defaults={'last_update': now()})

    @classmethod
    def last_change(cls):
        try:
            return cls.objects.get(ident=1).last_update
        except cls.DoesNotExist:
            pass


@python_2_unicode_compatible
class DjCeleryPeriodicTask(models.Model):
    name = models.CharField(
        _('name'), max_length=200, unique=True,
        help_text=_('Useful description'),
    )
    task = models.CharField(_('task name'), max_length=200)
    interval = models.ForeignKey(
        IntervalSchedule,
        null=True, blank=True, verbose_name=_('interval'),
        on_delete=models.CASCADE,
    )
    crontab = models.ForeignKey(
        CrontabSchedule, null=True, blank=True, verbose_name=_('crontab'),
        on_delete=models.CASCADE,
        help_text=_('Use one of interval/crontab'),
    )
    args = models.TextField(
        _('Arguments'), blank=True, default='[]',
        help_text=_('JSON encoded positional arguments'),
    )
    kwargs = models.TextField(
        _('Keyword arguments'), blank=True, default='{}',
        help_text=_('JSON encoded keyword arguments'),
    )
    queue = models.CharField(
        _('queue'), max_length=200, blank=True, null=True, default=None,
        help_text=_('Queue defined in CELERY_QUEUES'),
    )
    exchange = models.CharField(
        _('exchange'), max_length=200, blank=True, null=True, default=None,
    )
    routing_key = models.CharField(
        _('routing key'), max_length=200, blank=True, null=True, default=None,
    )
    expires = models.DateTimeField(
        _('expires'), blank=True, null=True,
    )
    enabled = models.BooleanField(
        _('enabled'), default=True,
    )
    last_run_at = models.DateTimeField(
        auto_now=False, auto_now_add=False,
        editable=False, blank=True, null=True,
    )
    total_run_count = models.PositiveIntegerField(
        default=0, editable=False,
    )
    date_changed = models.DateTimeField(auto_now=True)
    description = models.TextField(_('description'), blank=True)

    objects = managers.PeriodicTaskManager()
    no_changes = False

    class Meta:
        verbose_name = _('djcelery periodic task')
        verbose_name_plural = _('djcelery periodic tasks')

    def validate_unique(self, *args, **kwargs):
        super(DjCeleryPeriodicTask, self).validate_unique(*args, **kwargs)
        if not self.interval and not self.crontab:
            raise ValidationError(
                {'interval': ['One of interval or crontab must be set.']})
        if self.interval and self.crontab:
            raise ValidationError(
                {'crontab': ['Only one of interval or crontab must be set']})

    def save(self, *args, **kwargs):
        self.exchange = self.exchange or None
        self.routing_key = self.routing_key or None
        self.queue = self.queue or None
        if not self.enabled:
            self.last_run_at = None
        super(DjCeleryPeriodicTask, self).save(*args, **kwargs)

    def __str__(self):
        fmt = '{0.name}: {{no schedule}}'
        if self.interval:
            fmt = '{0.name}: {0.interval}'
        if self.crontab:
            fmt = '{0.name}: {0.crontab}'
        return fmt.format(self)

    @property
    def schedule(self):
        if self.interval:
            return self.interval.schedule
        if self.crontab:
            return self.crontab.schedule


signals.pre_delete.connect(DjCeleryPeriodicTasks.changed, sender=DjCeleryPeriodicTask)
signals.pre_save.connect(DjCeleryPeriodicTasks.changed, sender=DjCeleryPeriodicTask)


# Create your models here.
class PeriodicTaskManager(models.Manager):
    def create_task(self, name, template, cron, data, creator, timezone=None, extra_info=None, spread=False):
        snapshot, _ = Snapshot.objects.create_or_get_snapshot(data)
        schedule, _ = CrontabSchedule.objects.get_or_create(
            minute=cron.get('minute', '*'),
            hour=cron.get('hour', '*'),
            day_of_week=cron.get('day_of_week', '*'),
            day_of_month=cron.get('day_of_month', '*'),
            month_of_year=cron.get('month_of_year', '*'),
            timezone=timezone or 'UTC'
        )
        _ = schedule.schedule  # noqa

        task = self.create(
            name=name,
            template=template,
            snapshot=snapshot,
            cron=schedule.__str__(),
            creator=creator,
            extra_info=extra_info)

        kwargs = {
            'period_task_id': task.id,
            'spread': spread
        }
        celery_task = DjCeleryPeriodicTask.objects.create(
            crontab=schedule,
            name=uniqid(),
            task='pipeline.contrib.periodic_task.tasks.periodic_task_start',
            enabled=False,
            kwargs=json.dumps(kwargs))
        task.celery_task = celery_task
        task.save()
        return task


class PeriodicTask(models.Model):
    name = models.CharField(_(u"周期任务名称"), max_length=64)
    template = models.ForeignKey(
        PipelineTemplate,
        related_name='periodic_tasks',
        to_field='template_id',
        verbose_name=_(u"周期任务对应的模板"),
        null=True,
        on_delete=models.deletion.SET_NULL)
    cron = models.CharField(_(u"调度策略"), max_length=128)
    celery_task = models.ForeignKey(DjCeleryPeriodicTask, verbose_name=_(u"celery 周期任务实例"), null=True)
    snapshot = models.ForeignKey(
        Snapshot,
        related_name='periodic_tasks',
        verbose_name=_(u'用于创建流程实例的结构数据')
    )
    total_run_count = models.PositiveIntegerField(_(u"执行次数"), default=0)
    last_run_at = models.DateTimeField(_(u"上次运行时间"), null=True)
    creator = models.CharField(_(u'创建者'), max_length=32, default='')
    extra_info = CompressJSONField(verbose_name=_(u"额外信息"), null=True)

    objects = PeriodicTaskManager()

    def __unicode__(self):
        return u"{name}({id})".format(name=self.name, id=self.id)

    @property
    def enabled(self):
        return self.celery_task.enabled

    @property
    def execution_data(self):
        return self.snapshot.data

    @property
    def form(self):
        form = {key: var_info for key, var_info in self.execution_data['constants'].items() if
                var_info['show_type'] == 'show'}
        return form

    def delete(self, using=None):
        self.set_enabled(False)
        self.celery_task.delete()
        super(PeriodicTask, self).delete(using)
        PeriodicTaskHistory.objects.filter(periodic_task=self).delete()

    def set_enabled(self, enabled):
        self.celery_task.enabled = enabled
        self.celery_task.save()

    def modify_cron(self, cron, timezone=None):
        if self.enabled:
            raise InvalidOperationException('can not modify cron when task is enabled')
        schedule, _ = CrontabSchedule.objects.get_or_create(
            minute=cron.get('minute', '*'),
            hour=cron.get('hour', '*'),
            day_of_week=cron.get('day_of_week', '*'),
            day_of_month=cron.get('day_of_month', '*'),
            month_of_year=cron.get('month_of_year', '*'),
            timezone=timezone or 'UTC'
        )
        # try to initiate schedule object
        _ = schedule.schedule  # noqa
        self.cron = schedule.__str__()
        self.celery_task.crontab = schedule
        self.celery_task.save()
        self.save()

    def modify_constants(self, constants):
        if self.enabled:
            raise InvalidOperationException('can not modify constants when task is enabled')
        exec_data = self.execution_data
        for key, value in constants.items():
            if key in exec_data['constants']:
                exec_data['constants'][key]['value'] = value
        self.snapshot.data = exec_data
        self.snapshot.save()
        return exec_data['constants']


class PeriodicTaskHistoryManager(models.Manager):
    def record_schedule(self, periodic_task, pipeline_instance, ex_data, start_success=True):
        history = self.create(
            periodic_task=periodic_task,
            pipeline_instance=pipeline_instance,
            ex_data=ex_data,
            start_success=start_success
        )

        if not start_success:
            periodic_task_start_failed.send(
                sender=PeriodicTask,
                periodic_task=periodic_task,
                history=history
            )

        return history


class PeriodicTaskHistory(models.Model):
    periodic_task = models.ForeignKey(
        PeriodicTask,
        related_name='instance_rel',
        verbose_name=_(u"周期任务"),
        null=True)
    pipeline_instance = models.ForeignKey(
        PipelineInstance,
        related_name='periodic_task_rel',
        verbose_name=_(u"Pipeline 实例"),
        to_field='instance_id',
        null=True)
    ex_data = models.TextField(_(u"异常信息"))
    start_at = models.DateTimeField(_(u"开始时间"), auto_now_add=True)
    start_success = models.BooleanField(_(u"是否启动成功"), default=True)

    objects = PeriodicTaskHistoryManager()
