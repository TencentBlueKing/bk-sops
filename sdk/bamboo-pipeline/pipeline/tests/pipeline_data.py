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

# 存储 pipeline 结构的字典
pipeline_1 = {
    "id": "p1",  # 该 pipeline 的 id
    "name": "name",
    "start_event": {"id": "", "name": "", "type": "EmptyStartEvent", "incoming": None, "outgoing": "outgoing_flow_id"},
    "end_event": {"id": "", "name": "", "type": "EmptyEndEvent", "incoming": "incoming_flow_id", "outgoing": None},
    "activities": {  # 存放该 pipeline 中所有的 task，包含：起始任务，结束任务，子 pipeline
        "n1": {
            "id": "n1",
            "type": "ServiceActivity",
            "name": "",
            "incoming": "f1",
            "outgoing": "f2",
            "component": {
                "tag_code": "",
                "data": {
                    "env_id": {"hook": True, "constant": "${_env_id}", "value": ""},
                    "another_param": {"hook": True, "constant": "${_another_param}", "value": ""},
                },
            },
        },
        "n2": {"id": "n2", "type": "SubProcess", "name": "", "incoming": "f3", "outgoing": "f4", "template_id": ""},
    },
    "flows": {  # 存放该 Pipeline 中所有的线
        "f1": {"id": "f1", "source": "n1", "target": "n2", "is_default": False},
        "f2": {"id": "f2", "source": "n2", "target": "n3", "is_default": False},
    },
    "gateways": {  # 这里存放着网关的详细信息
        "g2": {
            "id": "g2",
            "type": "ExclusiveGateway",
            "name": "",
            "incoming": "flow_id_0",
            "outgoing": ["flow_id_1", "flow_id_2"],
            "data_source": "activity_id",
            "conditions": {
                "flow_id_1": {"evaluate": "result > 10"},  # 判断条件
                "flow_id_2": {"evaluate": "result < 10"},  # 判断条件
            },
            "converge_gateway_id": "converge_gateway_id",
        },
        "g3": {
            "id": "g3",
            "type": "ConvergeGateway",
            "name": "",
            "incoming": ["flow_id_3", "flow_id_4"],
            "outgoing": "flow_id_5",
        },
    },
    "constants": {  # 全局变量
        # '${_env_id}': {
        #     'name': '',
        #     'key': '${_env_id}',
        #     'desc': '',
        #     'tag_type': 'input_var',
        #     'validation': '^\d+$',
        #     'show_type': 'show',
        #     'tag_code': '${_env_id}',
        #     'value': '',
        #     'data': {
        #         'set': {
        #             'value': '${set}',
        #             'constant': '',
        #             'hook': 'off',
        #         },
        #         'module': {
        #             'value': '${module}',
        #             'constant': '',
        #             'hook': 'off',
        #         }
        #     }
        # },
        "${_env_id}": {
            "name": "",
            "key": "${_env_id}",
            "desc": "",
            "tag_type": "input_var",
            "validation": r"^\d+$",
            "show_type": "show",
            "tag_code": "${_env_id}",
            "value": "11",
        },
    },
}
