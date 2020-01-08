# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import mock

from django.test import TestCase

from pipeline.engine.models import ScheduleCeleryTask
from ..mock import *  # noqa


class TestScheduleCeleryTask(TestCase):
    def test_bind(self):
        schedule_id = '{}{}'.format(uniqid(), uniqid())
        celery_task_id = '{}{}'.format(uniqid(), uniqid())[: 40]

        ScheduleCeleryTask.objects.bind(schedule_id=schedule_id, celery_task_id=celery_task_id)
        task = ScheduleCeleryTask.objects.get(schedule_id=schedule_id, celery_task_id=celery_task_id)
        self.assertEqual(task.schedule_id, schedule_id)
        self.assertEqual(task.celery_task_id, celery_task_id)

        celery_task_id = '{}{}'.format(uniqid(), uniqid())[: 40]
        ScheduleCeleryTask.objects.bind(schedule_id=schedule_id, celery_task_id=celery_task_id)
        task.refresh_from_db()
        self.assertEqual(task.schedule_id, schedule_id)
        self.assertEqual(task.celery_task_id, celery_task_id)

    def test_unbind(self):
        schedule_id = '{}{}'.format(uniqid(), uniqid())
        celery_task_id = '{}{}'.format(uniqid(), uniqid())[: 40]

        ScheduleCeleryTask.objects.bind(schedule_id=schedule_id, celery_task_id=celery_task_id)
        task = ScheduleCeleryTask.objects.get(schedule_id=schedule_id, celery_task_id=celery_task_id)
        ScheduleCeleryTask.objects.unbind(schedule_id)
        task.refresh_from_db()
        self.assertEqual(task.celery_task_id, '')

    def test_destroy(self):
        schedule_id = '{}{}'.format(uniqid(), uniqid())
        celery_task_id = '{}{}'.format(uniqid(), uniqid())[: 40]

        ScheduleCeleryTask.objects.bind(schedule_id=schedule_id, celery_task_id=celery_task_id)
        ScheduleCeleryTask.objects.destroy(schedule_id)
        self.assertRaises(ScheduleCeleryTask.DoesNotExist, ScheduleCeleryTask.objects.get, schedule_id=schedule_id)

    def test_start_task(self):
        start_func = mock.MagicMock()
        celery_task_id = '{}{}'.format(uniqid(), uniqid())[: 40]
        start_func.return_value = celery_task_id
        schedule_id = '{}{}'.format(uniqid(), uniqid())
        kwargs = {'a': '1', 'b': 2}
        ScheduleCeleryTask.objects.start_task(schedule_id, start_func=start_func, kwargs=kwargs)
        start_func.assert_called_with(a='1', b=2)
        self.assertEqual(
            ScheduleCeleryTask.objects.filter(
                schedule_id=schedule_id,
                celery_task_id=start_func.return_value).count(),
            1)
