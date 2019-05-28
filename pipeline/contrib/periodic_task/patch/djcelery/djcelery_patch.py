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

import datetime
import logging

from django.db import connection
from celery import schedules
from celery.utils.log import get_logger
from celery import current_app
from djcelery.schedulers import ModelEntry, DatabaseScheduler
from djcelery.utils import make_aware
from anyjson import loads, dumps

from pipeline.contrib.periodic_task.models import (DjCeleryPeriodicTask,
                                                   DjCeleryPeriodicTasks,
                                                   CrontabSchedule,
                                                   IntervalSchedule)


def djcelry_upgrade():
    try:
        import djcelery
    except Exception:
        return

    # djcelery upgrate compatible
    # if djcelery version > 3.1.x
    if djcelery.__version__.split('.')[1] >= 2:
        with connection.cursor() as cursor:
            cursor.execute('show tables;')
            tables = {item[0] for item in cursor.fetchall()}
            is_first_migrate = 'django_migrations' not in tables
            if is_first_migrate:
                return

            using_djcelery = 'djcelery_taskstate' in tables
            if not using_djcelery:
                return

            # insert djcelery migration record
            cursor.execute('select * from `django_migrations` where app=\'djcelery\' and name=\'0001_initial\';')
            row = cursor.fetchall()
            if not row:
                cursor.execute('insert into `django_migrations` (app, name, applied) '
                               'values (\'djcelery\', \'0001_initial\', \'%s\');' %
                               datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))


class TzAwareModelEntry(ModelEntry):
    model_schedules = ((schedules.crontab, CrontabSchedule, 'crontab'),
                       (schedules.schedule, IntervalSchedule, 'interval'))
    save_fields = ['last_run_at', 'total_run_count', 'no_changes']

    def __init__(self, model):

        logger = get_logger(__name__)
        self.app = current_app._get_current_object()
        self.name = model.name
        self.task = model.task
        try:
            self.schedule = model.schedule
        except model.DoesNotExist:
            logger.error('Schedule was removed from database')
            logger.warning('Disabling %s', self.name)
            self._disable(model)
        try:
            self.args = loads(model.args or '[]')
            self.kwargs = loads(model.kwargs or '{}')
        except ValueError:
            logging.error('Failed to serialize arguments for %s.', self.name,
                          exc_info=1)
            logging.warning('Disabling %s', self.name)
            self._disable(model)

        self.options = {'queue': model.queue,
                        'exchange': model.exchange,
                        'routing_key': model.routing_key,
                        'expires': model.expires}
        self.total_run_count = model.total_run_count
        self.model = model

        if not model.last_run_at:
            model.last_run_at = self._default_now()
        self.last_run_at = make_aware(model.last_run_at)

    def _default_now(self):
        return self.schedule.now()

    @classmethod
    def from_entry(cls, name, skip_fields=('relative', 'options'), **entry):
        options = entry.get('options') or {}
        fields = dict(entry)
        for skip_field in skip_fields:
            fields.pop(skip_field, None)
        schedule = fields.pop('schedule')
        model_schedule, model_field = cls.to_model_schedule(schedule)

        # reset schedule
        for t in cls.model_schedules:
            fields[t[2]] = None

        fields[model_field] = model_schedule
        fields['args'] = dumps(fields.get('args') or [])
        fields['kwargs'] = dumps(fields.get('kwargs') or {})
        fields['queue'] = options.get('queue')
        fields['exchange'] = options.get('exchange')
        fields['routing_key'] = options.get('routing_key')
        obj, _ = DjCeleryPeriodicTask._default_manager.update_or_create(
            name=name, defaults=fields,
        )
        return cls(obj)


@classmethod
def create_or_update_task(cls, name, **schedule_dict):
    if 'schedule' not in schedule_dict:
        try:
            schedule_dict['schedule'] = \
                DjCeleryPeriodicTask._default_manager.get(name=name).schedule
        except DjCeleryPeriodicTask.DoesNotExist:
            pass
    cls.Entry.from_entry(name, **schedule_dict)


@classmethod
def delete_task(cls, name):
    DjCeleryPeriodicTask._default_manager.get(name=name).delete()


DatabaseScheduler.Entry = TzAwareModelEntry
DatabaseScheduler.Model = DjCeleryPeriodicTask
DatabaseScheduler.Changes = DjCeleryPeriodicTasks
DatabaseScheduler.create_or_update_task = create_or_update_task
DatabaseScheduler.delete_task = delete_task

djcelry_upgrade()
