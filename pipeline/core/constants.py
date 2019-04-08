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


class PipelineElement(object):
    ServiceActivity = 'ServiceActivity'
    LoopServiceActivity = 'LoopServiceActivity'
    SubProcess = 'SubProcess'
    ExclusiveGateway = 'ExclusiveGateway'
    ParallelGateway = 'ParallelGateway'
    ConditionalParallelGateway = 'ConditionalParallelGateway'
    ConvergeGateway = 'ConvergeGateway'
    EmptyStartEvent = 'EmptyStartEvent'
    EmptyEndEvent = 'EmptyEndEvent'

    pipeline = 'pipeline'
    id = 'id'
    type = 'type'
    start_event = 'start_event'
    end_event = 'end_event'
    activities = 'activities'
    flows = 'flows'
    gateways = 'gateways'
    constants = 'constants'
    conditions = 'conditions'
    incoming = 'incoming'
    outgoing = 'outgoing'
    source = 'source'
    target = 'target'
    data = 'data'
    component = 'component'
    evaluate = 'evaluate'
    name = 'name'
    inputs = 'inputs'
    outputs = 'outputs'
    source_act = 'source_act'
    source_key = 'source_key'
    code = 'code'
    error_ignorable = 'error_ignorable'
    skippable = 'skippable'
    can_retry = 'can_retry'
    timeout = 'timeout'
    loop_times = 'loop_times'
    converge_gateway_id = 'converge_gateway_id'
    is_param = 'is_param'
    value = 'value'
    params = 'params'
    is_default = 'is_default'
    optional = 'optional'
    template_id = 'template_id'
    plain = 'plain'
    splice = 'splice'
    lazy = 'lazy'

    location = 'location'
    line = 'line'


PE = PipelineElement()
