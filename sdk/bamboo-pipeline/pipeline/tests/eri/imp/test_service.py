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

from mock import MagicMock

from django.test import TestCase

from bamboo_engine.eri import ExecutionData, CallbackData, ScheduleType

from pipeline.core.flow.activity import Service, StaticIntervalGenerator, SquareIntervalGenerator
from pipeline.eri.imp.service import ServiceWrapper


class ServiceWrapperTestCase(TestCase):
    def test_pre_execute(self):
        service = MagicMock()
        service.pre_execute = MagicMock()
        data = ExecutionData(inputs={"1": 1}, outputs={"2": 2})
        root_pipeline_data = ExecutionData(inputs={"3": 3}, outputs={"4": 4})

        w = ServiceWrapper(service)
        w.pre_execute(data, root_pipeline_data)

        self.assertEqual(service.pre_execute.call_args[0][0].inputs, data.inputs)
        self.assertEqual(service.pre_execute.call_args[0][0].outputs, data.outputs)

    def test_pre_execute__no_define(self):
        service = MagicMock()
        service.pre_execute = None
        data = ExecutionData({}, {})
        root_pipeline_data = ExecutionData({}, {})

        w = ServiceWrapper(service)
        w.pre_execute(data, root_pipeline_data)

    def test_execute(self):
        class S(Service):
            def execute(self, data, parent_data):
                data.inputs.a = 1
                data.inputs.b = 2
                data.outputs.c = 3
                data.outputs.d = 4
                assert data.get_one_of_inputs("1") == 1
                assert data.get_one_of_outputs("2") == 2
                assert parent_data.get_one_of_inputs("3") == 3
                assert parent_data.get_one_of_outputs("4") == 4
                parent_data.inputs.e = 5
                parent_data.outputs.f = 6
                return False

        data = ExecutionData(inputs={"1": 1}, outputs={"2": 2})
        root_pipeline_data = ExecutionData(inputs={"3": 3}, outputs={"4": 4})

        w = ServiceWrapper(S())
        execute_res = w.execute(data, root_pipeline_data)

        self.assertFalse(execute_res)
        self.assertEqual(data.inputs, {"1": 1, "a": 1, "b": 2})
        self.assertEqual(data.outputs, {"2": 2, "c": 3, "d": 4})
        self.assertEqual(root_pipeline_data.inputs, {"3": 3})
        self.assertEqual(root_pipeline_data.outputs, {"4": 4})

    def test_schedule(self):
        class S(Service):
            def execute(self, data, parent_data):
                pass

            def schedule(self, data, parent_data, callback_data=None):
                data.inputs.a = 1
                data.inputs.b = 2
                data.outputs.c = 3
                data.outputs.d = 4
                assert data.get_one_of_inputs("1") == 1
                assert data.get_one_of_outputs("2") == 2
                assert parent_data.get_one_of_inputs("3") == 3
                assert parent_data.get_one_of_outputs("4") == 4
                assert callback_data == {"callback_data": "callback_data"}
                parent_data.inputs.e = 5
                parent_data.outputs.f = 6
                return False

        data = ExecutionData(inputs={"1": 1}, outputs={"2": 2})
        root_pipeline_data = ExecutionData(inputs={"3": 3}, outputs={"4": 4})
        callback_data = CallbackData(1, "", "", data={"callback_data": "callback_data"})
        schedule = MagicMock()

        w = ServiceWrapper(S())
        schedule_res = w.schedule(schedule, data, root_pipeline_data, callback_data)

        self.assertFalse(schedule_res)
        self.assertEqual(data.inputs, {"1": 1, "a": 1, "b": 2})
        self.assertEqual(data.outputs, {"2": 2, "c": 3, "d": 4})
        self.assertEqual(root_pipeline_data.inputs, {"3": 3})
        self.assertEqual(root_pipeline_data.outputs, {"4": 4})

    def test_need_schedule(self):
        class S1(Service):
            __need_schedule__ = True

            def execute(self, data, parent_data):
                pass

        class S2(Service):
            def execute(self, data, parent_data):
                pass

        self.assertTrue(ServiceWrapper(S1()).need_schedule())
        self.assertFalse(ServiceWrapper(S2()).need_schedule())

    def test_schedule_type(self):
        class S1(Service):
            def execute(self, data, parent_data):
                pass

        class S2(Service):
            __need_schedule__ = True
            interval = StaticIntervalGenerator(5)

            def execute(self, data, parent_data):
                pass

        class S3(Service):
            __need_schedule__ = True

            def execute(self, data, parent_data):
                pass

        class S4(Service):
            __need_schedule__ = True
            __multi_callback_enabled__ = True

            def execute(self, data, parent_data):
                pass

        self.assertEqual(ServiceWrapper(S1()).schedule_type(), None)
        self.assertEqual(ServiceWrapper(S2()).schedule_type(), ScheduleType.POLL)
        self.assertEqual(ServiceWrapper(S3()).schedule_type(), ScheduleType.CALLBACK)
        self.assertEqual(ServiceWrapper(S4()).schedule_type(), ScheduleType.MULTIPLE_CALLBACK)

    def test_is_schedule_done(self):
        class S(Service):
            __need_schedule__ = True

            def execute(self, data, parent_data):
                pass

        s = S()
        w = ServiceWrapper(s)

        self.assertFalse(w.is_schedule_done())
        s.finish_schedule()
        self.assertTrue(w.is_schedule_done())

    def test_schedule_after(self):
        class S1(Service):
            __need_schedule__ = True
            interval = StaticIntervalGenerator(5)

            def execute(self, data, parent_data):
                pass

        class S2(Service):
            __need_schedule__ = True
            interval = SquareIntervalGenerator()

            def execute(self, data, parent_data):
                pass

        schedule = MagicMock()

        w1 = ServiceWrapper(S1())
        w2 = ServiceWrapper(S2())
        data = MagicMock()
        root_pipeline_data = MagicMock()

        self.assertEqual(w1.schedule_after(None, data, root_pipeline_data), 5)
        self.assertEqual(w2.schedule_after(None, data, root_pipeline_data), 1)
        schedule.times = 10
        self.assertEqual(w1.schedule_after(schedule, data, root_pipeline_data), 5)
        self.assertEqual(w2.schedule_after(schedule, data, root_pipeline_data), 100)
