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


import threading

from django.test import TransactionTestCase

from bamboo_engine.eri.models import Schedule, ScheduleType

from pipeline.eri.models import Schedule as DBSchedule
from pipeline.eri.imp.schedule import ScheduleMixin


class ScheduleMixinTestCase(TransactionTestCase):
    def setUp(self):
        self.mixin = ScheduleMixin()
        self.process_id = 99
        self.node_id = "nid"
        self.version = "v1"
        self.schedule_type = ScheduleType.POLL
        self.schedule = DBSchedule.objects.create(
            process_id=self.process_id, node_id=self.node_id, version="v2", type=self.schedule_type.value
        )

    def test_set_schedule(self):
        schedule = self.mixin.set_schedule(
            process_id=self.process_id, node_id=self.node_id, version=self.version, schedule_type=self.schedule_type
        )
        schedule_model = DBSchedule.objects.get(id=schedule.id)

        self.assertTrue(schedule, Schedule)
        self.assertEqual(schedule.id, schedule_model.id)
        self.assertEqual(schedule.type, self.schedule_type)
        self.assertEqual(schedule.process_id, self.process_id)
        self.assertEqual(schedule.node_id, self.node_id)
        self.assertEqual(schedule.finished, False)
        self.assertEqual(schedule.expired, False)
        self.assertEqual(schedule.version, self.version)
        self.assertEqual(schedule.times, 0)

        self.assertEqual(schedule_model.type, self.schedule_type.value)
        self.assertEqual(schedule_model.process_id, self.process_id)
        self.assertEqual(schedule_model.node_id, self.node_id)
        self.assertEqual(schedule_model.finished, False)
        self.assertEqual(schedule_model.expired, False)
        self.assertEqual(schedule_model.scheduling, False)
        self.assertEqual(schedule_model.version, self.version)
        self.assertEqual(schedule_model.schedule_times, 0)

    def test_get_schedule(self):
        schedule = self.mixin.get_schedule(self.schedule.id)

        self.assertTrue(isinstance(schedule, Schedule))
        self.assertEqual(schedule.id, self.schedule.id)
        self.assertEqual(schedule.type, ScheduleType(self.schedule.type))
        self.assertEqual(schedule.process_id, self.schedule.process_id)
        self.assertEqual(schedule.node_id, self.schedule.node_id)
        self.assertEqual(schedule.finished, self.schedule.finished)
        self.assertEqual(schedule.expired, self.schedule.expired)
        self.assertEqual(schedule.version, self.schedule.version)
        self.assertEqual(schedule.times, self.schedule.schedule_times)

    def test_get_schedule_with_node_and_version(self):
        schedule = self.mixin.get_schedule_with_node_and_version(self.schedule.node_id, self.schedule.version)

        self.assertTrue(isinstance(schedule, Schedule))
        self.assertEqual(schedule.id, self.schedule.id)
        self.assertEqual(schedule.type, ScheduleType(self.schedule.type))
        self.assertEqual(schedule.process_id, self.schedule.process_id)
        self.assertEqual(schedule.node_id, self.schedule.node_id)
        self.assertEqual(schedule.finished, self.schedule.finished)
        self.assertEqual(schedule.expired, self.schedule.expired)
        self.assertEqual(schedule.version, self.schedule.version)
        self.assertEqual(schedule.times, self.schedule.schedule_times)

    def test_get_schedule_with_node_and_version_not_exist(self):
        self.assertRaises(
            DBSchedule.DoesNotExist, self.mixin.get_schedule_with_node_and_version, self.schedule.node_id, "not_exist",
        )

    def test_apply_schedule_lock(self):
        schedule_count = 10

        lock = threading.Lock()
        res = {False: 0, True: 0}

        def target(schedule_id):
            success = self.mixin.apply_schedule_lock(schedule_id)
            lock.acquire()
            res[success] += 1
            lock.release()

        threads = [threading.Thread(target=target, args=(self.schedule.id,)) for i in range(schedule_count)]

        for t in threads:
            t.start()

        for t in threads:
            t.join(1)

        self.schedule.refresh_from_db()

        self.assertTrue(self.schedule.scheduling)
        self.assertEqual(res[False], schedule_count - 1)
        self.assertEqual(res[True], 1)

    def test_apply_schedule_lock__all_fail(self):
        self.schedule.scheduling = True
        self.schedule.save()
        schedule_count = 10

        lock = threading.Lock()
        res = {False: 0, True: 0}

        def target(schedule_id):
            success = self.mixin.apply_schedule_lock(schedule_id)
            lock.acquire()
            res[success] += 1
            lock.release()

        threads = [threading.Thread(target=target, args=(self.schedule.id,)) for i in range(schedule_count)]

        for t in threads:
            t.start()

        for t in threads:
            t.join(1)

        self.schedule.refresh_from_db()

        self.assertTrue(self.schedule.scheduling)
        self.assertEqual(res[False], schedule_count)
        self.assertEqual(res[True], 0)

    def test_release_schedule_lock(self):
        self.schedule.scheduling = True
        self.schedule.save()
        schedule_count = 10

        def target(schedule_id):
            self.mixin.release_schedule_lock(schedule_id)

        threads = [threading.Thread(target=target, args=(self.schedule.id,)) for i in range(schedule_count)]

        for t in threads:
            t.start()

        for t in threads:
            t.join(1)

        self.schedule.refresh_from_db()

        self.assertFalse(self.schedule.scheduling)

    def test_expire_schedule(self):
        self.assertFalse(self.schedule.expired)
        self.mixin.expire_schedule(self.schedule.id)
        self.schedule.refresh_from_db()
        self.assertTrue(self.schedule.expired)

    def test_finish_schedule(self):
        self.assertFalse(self.schedule.finished)
        self.mixin.finish_schedule(self.schedule.id)
        self.schedule.refresh_from_db()
        self.assertTrue(self.schedule.finished)

    def test_add_schedule_times(self):
        self.assertEqual(self.schedule.schedule_times, 0)
        self.mixin.add_schedule_times(self.schedule.id)
        self.mixin.add_schedule_times(self.schedule.id)
        self.mixin.add_schedule_times(self.schedule.id)
        self.schedule.refresh_from_db()
        self.assertEqual(self.schedule.schedule_times, 3)
