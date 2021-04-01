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
from mock import MagicMock

from pipeline.core.flow.activity import ServiceActivity, SubProcess
from pipeline.core.flow.event import EmptyEndEvent, EmptyStartEvent, ExecutableEndEvent
from pipeline.core.flow.gateway import ConditionalParallelGateway, ConvergeGateway, ExclusiveGateway, ParallelGateway
from pipeline.engine.core.handlers import HandlersFactory
from pipeline.engine.core.handlers.conditional_parallel import ConditionalParallelGatewayHandler
from pipeline.engine.core.handlers.converge_gateway import ConvergeGatewayHandler
from pipeline.engine.core.handlers.empty_start_event import EmptyStartEventHandler
from pipeline.engine.core.handlers.endevent import EmptyEndEventHandler, ExecutableEndEventHandler
from pipeline.engine.core.handlers.exclusive_gateway import ExclusiveGatewayHandler
from pipeline.engine.core.handlers.parallel_gateway import ParallelGatewayHandler
from pipeline.engine.core.handlers.service_activity import ServiceActivityHandler
from pipeline.engine.core.handlers.subprocess import SubprocessHandler


class CustomEndEventOne(ExecutableEndEvent):
    def execute(self, in_subprocess, root_pipeline_id, current_pipeline_id):
        pass


class CustomEndEventTwo(ExecutableEndEvent):
    def execute(self, in_subprocess, root_pipeline_id, current_pipeline_id):
        pass


class EngineHandlerTestCase(TestCase):
    def setUp(self):
        self.empty_start_event = EmptyStartEvent(id="1")
        self.empty_end_event = EmptyEndEvent(id="2")
        self.service_activity = ServiceActivity(id="3", service=None)
        self.subprocess = SubProcess(id="4", pipeline=MagicMock())
        self.exclusive_gateway = ExclusiveGateway(id="5")
        self.parallel_gateway = ParallelGateway(id="6", converge_gateway_id=None)
        self.conditional_parallel_gateway = ConditionalParallelGateway(id="7", converge_gateway_id=None)
        self.converge_gateway = ConvergeGateway(id="8")
        self.executable_end_event_1 = CustomEndEventOne(id="9")
        self.executable_end_event_2 = CustomEndEventTwo(id="9")

    def test_handlers_for(self):
        self.assertIsInstance(HandlersFactory.handlers_for(self.empty_start_event), EmptyStartEventHandler)
        self.assertIsInstance(HandlersFactory.handlers_for(self.empty_end_event), EmptyEndEventHandler)
        self.assertIsInstance(HandlersFactory.handlers_for(self.service_activity), ServiceActivityHandler)
        self.assertIsInstance(HandlersFactory.handlers_for(self.subprocess), SubprocessHandler)
        self.assertIsInstance(HandlersFactory.handlers_for(self.exclusive_gateway), ExclusiveGatewayHandler)
        self.assertIsInstance(HandlersFactory.handlers_for(self.parallel_gateway), ParallelGatewayHandler)
        self.assertIsInstance(
            HandlersFactory.handlers_for(self.conditional_parallel_gateway), ConditionalParallelGatewayHandler
        )
        self.assertIsInstance(HandlersFactory.handlers_for(self.converge_gateway), ConvergeGatewayHandler)
        self.assertIsInstance(HandlersFactory.handlers_for(self.executable_end_event_1), ExecutableEndEventHandler)
        self.assertIsInstance(HandlersFactory.handlers_for(self.executable_end_event_2), ExecutableEndEventHandler)

    def test_find_cluster_root_cls(self):
        self.assertEqual(HandlersFactory.find_cluster_root_cls(self.empty_start_event), EmptyStartEvent)
        self.assertEqual(HandlersFactory.find_cluster_root_cls(self.empty_end_event), EmptyEndEvent)
        self.assertEqual(HandlersFactory.find_cluster_root_cls(self.service_activity), ServiceActivity)
        self.assertEqual(HandlersFactory.find_cluster_root_cls(self.subprocess), SubProcess)
        self.assertEqual(HandlersFactory.find_cluster_root_cls(self.exclusive_gateway), ExclusiveGateway)
        self.assertEqual(HandlersFactory.find_cluster_root_cls(self.parallel_gateway), ParallelGateway)
        self.assertEqual(
            HandlersFactory.find_cluster_root_cls(self.conditional_parallel_gateway), ConditionalParallelGateway
        )
        self.assertEqual(HandlersFactory.find_cluster_root_cls(self.converge_gateway), ConvergeGateway)
        self.assertEqual(HandlersFactory.find_cluster_root_cls(self.executable_end_event_1), ExecutableEndEvent)
        self.assertEqual(HandlersFactory.find_cluster_root_cls(self.executable_end_event_2), ExecutableEndEvent)
