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

from pipeline.core.constants import PE

MIN_LEN = 1
DUMMY_NODE_TYPE = 'DummyNode'
DUMMY_FLOW_TYPE = 'DummyFlow'

CANVAS_WIDTH = 1300
POSITION = {
    'activity_size': (150, 42),
    'event_size': (42, 42),
    'gateway_size': (32, 32),
    'start': (60, 100)
}
PIPELINE_ELEMENT_TO_WEB = {
    DUMMY_NODE_TYPE: DUMMY_NODE_TYPE,
    PE.ServiceActivity: 'tasknode',
    PE.SubProcess: 'subflow',
    PE.EmptyStartEvent: 'startpoint',
    PE.EmptyEndEvent: 'endpoint',
    PE.ExclusiveGateway: 'branchgateway',
    PE.ParallelGateway: 'parallelgateway',
    PE.ConvergeGateway: 'convergegateway'
}
PIPELINE_WEB_TO_ELEMENT = {value: key for key, value in PIPELINE_ELEMENT_TO_WEB.items()}
FLOW_ARROW = {
    'left': 'Left',
    'right': 'Right',
    'bottom': 'Bottom',
    'top': 'Top'
}
