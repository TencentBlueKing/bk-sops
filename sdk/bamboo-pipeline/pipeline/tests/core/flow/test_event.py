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

from pipeline.core.flow.event import *  # noqa


class TestEvent(TestCase):
    def test_event(self):
        event_id = "1"
        event = Event(event_id)
        self.assertTrue(isinstance(event, FlowNode))
        self.assertEqual(event_id, event.id)

    def test_throw_event(self):
        event_id = "1"
        event = ThrowEvent(event_id)
        self.assertTrue(isinstance(event, Event))

    def test_catch_event(self):
        event_id = "1"
        event = CatchEvent(event_id)
        self.assertTrue(isinstance(event, Event))

    def test_start_event(self):
        event_id = "1"
        event = StartEvent(event_id)
        self.assertTrue(isinstance(event, CatchEvent))

    def test_end_event(self):
        event_id = "1"
        event = EndEvent(event_id)
        self.assertTrue(isinstance(event, ThrowEvent))

    def test_empty_start_event(self):
        event_id = "1"
        event = EmptyStartEvent(event_id)
        self.assertTrue(isinstance(event, StartEvent))

    def test_empty_end_event(self):
        event_id = "1"
        event = EmptyEndEvent(event_id)
        self.assertTrue(isinstance(event, EndEvent))
