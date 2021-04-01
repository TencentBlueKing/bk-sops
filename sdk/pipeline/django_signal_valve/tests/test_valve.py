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
from pipeline.django_signal_valve.models import Signal
from pipeline.django_signal_valve.tests import mock_signal


class TestValve(TestCase):
    def setUp(self):
        valve.unload_valve_function()

    def test_set_valve_function(self):
        self.assertRaises(Exception, valve.set_valve_function, args=[1])

        def func():
            return True

        valve.unload_valve_function()
        valve.set_valve_function(func)
        self.assertEqual(valve.valve_function(), func)
        self.assertRaises(Exception, valve.set_valve_function, args=[func])

        valve.__valve_function = None

    def test_send_on_valve_is_none(self):
        kwargs_1 = {"1": 1}
        kwargs_2 = {"2": 2}

        valve.unload_valve_function()
        valve.send(mock_signal, "signal_1", **kwargs_1)
        valve.send(mock_signal, "signal_1", **kwargs_2)
        self.assertEqual(mock_signal.signal_1.history[0], kwargs_1)
        self.assertEqual(mock_signal.signal_1.history[1], kwargs_2)

        mock_signal.clear()

    def test_send_on_valve_opened(self):
        kwargs_1 = {"1": 1}
        kwargs_2 = {"2": 2}

        def is_valve_closed():
            return False

        valve.unload_valve_function()
        valve.set_valve_function(is_valve_closed)
        valve.send(mock_signal, "signal_1", **kwargs_1)
        valve.send(mock_signal, "signal_1", **kwargs_2)
        self.assertEqual(mock_signal.signal_1.history[0], kwargs_1)
        self.assertEqual(mock_signal.signal_1.history[1], kwargs_2)

        mock_signal.clear()

    def test_send_on_closed(self):
        kwargs_1 = {"1": 1}
        kwargs_2 = {"2": 2}

        def is_valve_closed():
            return True

        valve.unload_valve_function()
        valve.set_valve_function(is_valve_closed)
        valve.send(mock_signal, "signal_1", **kwargs_1)
        valve.send(mock_signal, "signal_1", **kwargs_2)
        self.assertEqual(len(mock_signal.signal_1.history), 0)

        mock_signal.clear()
        Signal.objects.all().delete()

    def test_open_valve(self):
        kwargs_1 = {"1": 1}
        kwargs_2 = {"2": 2}

        def valve_closed():
            return True

        valve.unload_valve_function()
        valve.set_valve_function(valve_closed)
        valve.send(mock_signal, "signal_1", **kwargs_1)
        valve.send(mock_signal, "signal_1", **kwargs_2)
        self.assertEqual(len(mock_signal.signal_1.history), 0)
        valve.open_valve(mock_signal)
        self.assertEqual(mock_signal.signal_1.history[0], kwargs_1)
        self.assertEqual(mock_signal.signal_1.history[1], kwargs_2)

        mock_signal.clear()
