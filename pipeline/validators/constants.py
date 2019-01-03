# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
MAX_IN = 1000
MAX_OUT = 1000
FLOW_NODES_WITHOUT_STARTEVENT = [
    "ServiceActivity",
    "SubProcess",
    "ExclusiveGateway",
    "ParallelGateway",
    "ConvergeGateway",
    "EmptyEndEvent",
]

# rules of activity graph
ACTIVITY_RULES = {
    "EmptyStartEvent": {
        "min_in": 0,
        "max_in": 0,
        "min_out": 1,
        "max_out": 1,
        "allowed_out": ["ServiceActivity", "ExclusiveGateway", "ParallelGateway", "EmptyEndEvent", "SubProcess"]
    },
    "EmptyEndEvent": {
        "min_in": 1,
        "max_in": MAX_IN,
        "min_out": 0,
        "max_out": 0,
        "allowed_out": []
    },
    "ServiceActivity": {
        "min_in": 1,
        "max_in": 1,
        "min_out": 1,
        "max_out": 1,
        "allowed_out": FLOW_NODES_WITHOUT_STARTEVENT
    },
    "ExclusiveGateway": {
        "min_in": 1,
        "max_in": 1,
        "min_out": 2,
        "max_out": MAX_OUT,
        "allowed_out": FLOW_NODES_WITHOUT_STARTEVENT
    },
    "ParallelGateway": {
        "min_in": 1,
        "max_in": 1,
        "min_out": 2,
        "max_out": MAX_OUT,
        "allowed_out": FLOW_NODES_WITHOUT_STARTEVENT
    },
    "ConvergeGateway": {
        "min_in": 2,
        "max_in": MAX_OUT,
        "min_out": 1,
        "max_out": 1,
        "allowed_out": FLOW_NODES_WITHOUT_STARTEVENT

    },
    "SubProcess": {
        "min_in": 1,
        "max_in": 1,
        "min_out": 1,
        "max_out": 1,
        "allowed_out": FLOW_NODES_WITHOUT_STARTEVENT
    }
}
