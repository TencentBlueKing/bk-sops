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

from django.test import TestCase

from pipeline.core.flow.event import EmptyStartEvent, EmptyEndEvent
from pipeline.core.flow.activity import ServiceActivity, SubProcess
from pipeline.core.flow.gateway import ExclusiveGateway, ParallelGateway, ConditionalParallelGateway, ConvergeGateway

from pipeline.engine.core import handlers


class EngineHandlerTestCase(TestCase):

    def test_node_handler(self):
        self.assertIsInstance(handlers.FLOW_NODE_HANDLERS[EmptyStartEvent], handlers.EmptyStartEventHandler)
        self.assertIsInstance(handlers.FLOW_NODE_HANDLERS[EmptyEndEvent], handlers.EmptyEndEventHandler)
        self.assertIsInstance(handlers.FLOW_NODE_HANDLERS[ServiceActivity], handlers.ServiceActivityHandler)
        self.assertIsInstance(handlers.FLOW_NODE_HANDLERS[SubProcess], handlers.SubprocessHandler)
        self.assertIsInstance(handlers.FLOW_NODE_HANDLERS[ExclusiveGateway], handlers.ExclusiveGatewayHandler)
        self.assertIsInstance(handlers.FLOW_NODE_HANDLERS[ParallelGateway], handlers.ParallelGatewayHandler)
        self.assertIsInstance(handlers.FLOW_NODE_HANDLERS[ConditionalParallelGateway],
                              handlers.ConditionalParallelGatewayHandler)
        self.assertIsInstance(handlers.FLOW_NODE_HANDLERS[ConvergeGateway], handlers.ConvergeGatewayHandler)
