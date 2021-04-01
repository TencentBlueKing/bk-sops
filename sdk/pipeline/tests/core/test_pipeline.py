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

from pipeline.core.data.base import DataObject
from pipeline.core.flow.activity import ServiceActivity
from pipeline.core.flow.base import SequenceFlow
from pipeline.core.flow.event import EmptyEndEvent, EmptyStartEvent
from pipeline.core.pipeline import *  # noqa


class TestPipeline(TestCase):
    def test_node(self):
        start_event = EmptyStartEvent(id="a")
        act = ServiceActivity(id="b", service=None, data=DataObject({}))
        end_event = EmptyEndEvent(id="c")

        flow_ab = SequenceFlow("ab", start_event, act)
        flow_bc = SequenceFlow("bc", act, end_event)

        start_event.outgoing.add_flow(flow_ab)
        act.incoming.add_flow(flow_ab)
        act.outgoing.add_flow(flow_bc)
        end_event.incoming.add_flow(flow_bc)

        spec = PipelineSpec(start_event, end_event, [flow_ab, flow_bc], [act], [], None, None)
        pipeline = Pipeline("pipeline", spec)
        self.assertEqual(act, pipeline.node("b"))

    def test_start_event(self):
        start_event = EmptyStartEvent(id="a")
        act = ServiceActivity(id="b", service=None, data=DataObject({}))
        end_event = EmptyEndEvent(id="c")

        flow_ab = SequenceFlow("ab", start_event, act)
        flow_bc = SequenceFlow("bc", act, end_event)

        start_event.outgoing.add_flow(flow_ab)
        act.incoming.add_flow(flow_ab)
        act.outgoing.add_flow(flow_bc)
        end_event.incoming.add_flow(flow_bc)

        spec = PipelineSpec(start_event, end_event, [flow_ab, flow_bc], [act], [], None, None)
        pipeline = Pipeline("pipeline", spec)
        self.assertEqual(start_event, pipeline.start_event)

    def test_end_event(self):
        start_event = EmptyStartEvent(id="a")
        act = ServiceActivity(id="b", service=None, data=DataObject({}))
        end_event = EmptyEndEvent(id="c")

        flow_ab = SequenceFlow("ab", start_event, act)
        flow_bc = SequenceFlow("bc", act, end_event)

        start_event.outgoing.add_flow(flow_ab)
        act.incoming.add_flow(flow_ab)
        act.outgoing.add_flow(flow_bc)
        end_event.incoming.add_flow(flow_bc)

        spec = PipelineSpec(start_event, end_event, [flow_ab, flow_bc], [act], [], None, None)
        pipeline = Pipeline("pipeline", spec)
        self.assertEqual(end_event, pipeline.end_event)
