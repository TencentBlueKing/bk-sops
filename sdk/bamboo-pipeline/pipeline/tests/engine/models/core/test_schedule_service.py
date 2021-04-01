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

from django.test import TestCase

from pipeline.django_signal_valve import valve
from pipeline.engine import signals
from pipeline.engine.exceptions import InvalidOperationException
from pipeline.engine.models import ScheduleCeleryTask, ScheduleService

from ..mock import *  # noqa

valve.unload_valve_function()


class TestScheduleService(TestCase):
    @mock.patch("pipeline.django_signal_valve.valve.send", mock.MagicMock())
    @mock.patch("pipeline.engine.core.data.set_schedule_data", mock.MagicMock())
    def test_set_schedule(self):
        from pipeline.django_signal_valve.valve import send
        from pipeline.engine.core.data import set_schedule_data

        service_act = ServiceActObject(interval=None)
        process_id = uniqid()
        version = uniqid()
        parent_data = "parent_data"
        schedule = ScheduleService.objects.set_schedule(
            activity_id=service_act.id,
            service_act=service_act,
            process_id=process_id,
            version=version,
            parent_data=parent_data,
        )
        self.assertEqual(schedule.id, "{}{}".format(service_act.id, version))
        self.assertEqual(schedule.activity_id, service_act.id)
        self.assertEqual(schedule.process_id, process_id)
        self.assertEqual(schedule.wait_callback, True)
        self.assertEqual(schedule.version, version)
        set_schedule_data.assert_called_with(schedule.id, parent_data)

        # service need callback
        set_schedule_data.reset_mock()
        interval = StaticIntervalObject(interval=3)
        service_act = ServiceActObject(interval=interval)
        process_id = uniqid()
        version = uniqid()
        parent_data = "new_parent_data"
        schedule = ScheduleService.objects.set_schedule(
            activity_id=service_act.id,
            service_act=service_act,
            process_id=process_id,
            version=version,
            parent_data=parent_data,
        )
        self.assertEqual(schedule.id, "{}{}".format(service_act.id, version))
        self.assertEqual(schedule.activity_id, service_act.id)
        self.assertEqual(schedule.process_id, process_id)
        self.assertEqual(schedule.wait_callback, False)
        self.assertEqual(schedule.version, version)
        set_schedule_data.assert_called_with(schedule.id, parent_data)
        send.assert_called_with(
            signals,
            "schedule_ready",
            sender=ScheduleService,
            process_id=process_id,
            schedule_id=schedule.id,
            countdown=interval.interval,
        )

    @mock.patch("pipeline.django_signal_valve.valve.send", mock.MagicMock())
    @mock.patch("pipeline.engine.core.data.set_schedule_data", mock.MagicMock())
    def test_schedule_for(self):
        service_act = ServiceActObject(interval=None)
        process_id = uniqid()
        version = uniqid()
        parent_data = "parent_data"
        ScheduleService.objects.set_schedule(
            activity_id=service_act.id,
            service_act=service_act,
            process_id=process_id,
            version=version,
            parent_data=parent_data,
        )
        schedule = ScheduleService.objects.schedule_for(activity_id=service_act.id, version=version)
        self.assertEqual(schedule.id, "{}{}".format(service_act.id, version))

    @mock.patch("pipeline.django_signal_valve.valve.send", mock.MagicMock())
    @mock.patch("pipeline.engine.core.data.set_schedule_data", mock.MagicMock())
    def test_delete_schedule(self):
        service_act = ServiceActObject(interval=None)
        process_id = uniqid()
        version = uniqid()
        parent_data = "parent_data"
        ScheduleService.objects.set_schedule(
            activity_id=service_act.id,
            service_act=service_act,
            process_id=process_id,
            version=version,
            parent_data=parent_data,
        )
        ScheduleService.objects.delete_schedule(activity_id=service_act.id, version=version)
        self.assertRaises(
            ScheduleService.DoesNotExist,
            ScheduleService.objects.schedule_for,
            activity_id=service_act.id,
            version=version,
        )

    @mock.patch("pipeline.django_signal_valve.valve.send", mock.MagicMock())
    @mock.patch("pipeline.engine.core.data.set_schedule_data", mock.MagicMock())
    @mock.patch("pipeline.engine.models.ScheduleCeleryTask.objects.unbind", mock.MagicMock())
    def test_set_next_schedule(self):
        from pipeline.django_signal_valve.valve import send

        interval = StaticIntervalObject(interval=3)
        service_act = ServiceActObject(interval=interval)
        process_id = uniqid()
        version = uniqid()
        parent_data = "new_parent_data"
        schedule = ScheduleService.objects.set_schedule(
            activity_id=service_act.id,
            service_act=service_act,
            process_id=process_id,
            version=version,
            parent_data=parent_data,
        )

        schedule.is_scheduling = True
        schedule.save()
        schedule.set_next_schedule()
        schedule.refresh_from_db()
        self.assertFalse(schedule.is_scheduling)
        send.assert_called_with(
            signals,
            "schedule_ready",
            sender=ScheduleService,
            process_id=process_id,
            schedule_id=schedule.id,
            countdown=interval.interval,
        )
        ScheduleCeleryTask.objects.unbind.assert_called_with(schedule.id)

        # test invalid call
        service_act = ServiceActObject(interval=None)
        process_id = uniqid()
        version = uniqid()
        parent_data = "new_parent_data"
        schedule = ScheduleService.objects.set_schedule(
            activity_id=service_act.id,
            service_act=service_act,
            process_id=process_id,
            version=version,
            parent_data=parent_data,
        )
        self.assertRaises(InvalidOperationException, schedule.set_next_schedule)

    @mock.patch("pipeline.django_signal_valve.valve.send", mock.MagicMock())
    @mock.patch("pipeline.engine.core.data.set_schedule_data", mock.MagicMock())
    @mock.patch("pipeline.engine.core.data.delete_parent_data", mock.MagicMock())
    @mock.patch("pipeline.engine.models.ScheduleCeleryTask.objects.destroy", mock.MagicMock())
    def test_destroy(self):
        from pipeline.engine.core.data import delete_parent_data

        interval = StaticIntervalObject(interval=3)
        service_act = ServiceActObject(interval=interval)
        process_id = uniqid()
        version = uniqid()
        parent_data = "new_parent_data"
        schedule = ScheduleService.objects.set_schedule(
            activity_id=service_act.id,
            service_act=service_act,
            process_id=process_id,
            version=version,
            parent_data=parent_data,
        )

        schedule_id = schedule.id
        schedule.destroy()
        self.assertRaises(ScheduleService.DoesNotExist, ScheduleService.objects.get, id=schedule_id)
        delete_parent_data.assert_called_with(schedule_id)
        ScheduleCeleryTask.objects.destroy.assert_called_with(schedule_id)

    @mock.patch("pipeline.django_signal_valve.valve.send", mock.MagicMock())
    @mock.patch("pipeline.engine.models.ScheduleCeleryTask.objects.destroy", mock.MagicMock())
    @mock.patch("pipeline.engine.core.data.set_schedule_data", mock.MagicMock())
    def test_finish(self):
        interval = StaticIntervalObject(interval=3)
        service_act = ServiceActObject(interval=interval)
        process_id = uniqid()
        version = uniqid()
        parent_data = "new_parent_data"
        schedule = ScheduleService.objects.set_schedule(
            activity_id=service_act.id,
            service_act=service_act,
            process_id=process_id,
            version=version,
            parent_data=parent_data,
        )
        schedule.finish()

        self.assertTrue(schedule.is_finished)
        self.assertIsNone(schedule.service_act)
        self.assertFalse(schedule.is_scheduling)
        ScheduleCeleryTask.objects.destroy.assert_called_with(schedule.id)

    @mock.patch("pipeline.django_signal_valve.valve.send", mock.MagicMock())
    @mock.patch("pipeline.engine.core.data.set_schedule_data", mock.MagicMock())
    def test_callback(self):
        from pipeline.django_signal_valve.valve import send

        service_act = ServiceActObject(interval=None)
        process_id = uniqid()
        version = uniqid()
        parent_data = "new_parent_data"
        callback_data = "callback_data"
        schedule = ScheduleService.objects.set_schedule(
            activity_id=service_act.id,
            service_act=service_act,
            process_id=process_id,
            version=version,
            parent_data=parent_data,
        )
        schedule.callback(callback_data, process_id)

        self.assertEqual(schedule.callback_data, callback_data)
        send.assert_called_with(
            signals,
            "schedule_ready",
            sender=ScheduleService,
            process_id=process_id,
            schedule_id=schedule.id,
            countdown=0,
        )

        # test invalid callback
        service_act = ServiceActObject(interval=StaticIntervalObject(interval=1))
        process_id = uniqid()
        version = uniqid()
        parent_data = "new_parent_data"
        callback_data = "callback_data"
        schedule = ScheduleService.objects.set_schedule(
            activity_id=service_act.id,
            service_act=service_act,
            process_id=process_id,
            version=version,
            parent_data=parent_data,
        )
        self.assertRaises(
            InvalidOperationException, schedule.callback, callback_data=callback_data, process_id=process_id
        )
