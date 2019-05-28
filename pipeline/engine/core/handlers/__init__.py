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

from service_activity import ServiceActivityHandler
from subprocess import SubprocessHandler
from empty_start_event import EmptyStartEventHandler
from empty_end_event import EmptyEndEventHandler
from exclusive_gateway import ExclusiveGatewayHandler
from parallel_gateway import ParallelGatewayHandler
from conditional_parallel import ConditionalParallelGatewayHandler
from converge_gateway import ConvergeGatewayHandler

FLOW_NODE_HANDLERS = {
    EmptyStartEventHandler.element_cls(): EmptyStartEventHandler(),
    EmptyEndEventHandler.element_cls(): EmptyEndEventHandler(),
    ServiceActivityHandler.element_cls(): ServiceActivityHandler(),
    SubprocessHandler.element_cls(): SubprocessHandler(),
    ExclusiveGatewayHandler.element_cls(): ExclusiveGatewayHandler(),
    ParallelGatewayHandler.element_cls(): ParallelGatewayHandler(),
    ConditionalParallelGatewayHandler.element_cls(): ConditionalParallelGatewayHandler(),
    ConvergeGatewayHandler.element_cls(): ConvergeGatewayHandler()
}
