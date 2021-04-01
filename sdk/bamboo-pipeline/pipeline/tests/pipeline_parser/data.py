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

import copy

from pipeline.utils.uniqid import node_uniqid

id_list = [node_uniqid() for i in range(10)]
PIPELINE_DATA = {
    "id": id_list[0],
    "name": "name",
    "start_event": {
        "id": id_list[1],
        "name": "start",
        "type": "EmptyStartEvent",
        "incoming": None,
        "outgoing": id_list[5],
    },
    "end_event": {"id": id_list[2], "name": "end", "type": "EmptyEndEvent", "incoming": id_list[7], "outgoing": None},
    "activities": {
        id_list[3]: {
            "id": id_list[3],
            "type": "ServiceActivity",
            "name": "first_task",
            "incoming": id_list[5],
            "outgoing": id_list[6],
            "component": {
                "code": "test",
                "inputs": {
                    "input_test": {"type": "plain", "value": "custom2"},
                    "radio_test": {"type": "plain", "value": "1"},
                },
                "global_outputs": {"key1": "${global_key1}"},
            },
        },
        id_list[4]: {
            "id": id_list[4],
            "type": "ServiceActivity",
            "name": "first_task",
            "incoming": id_list[6],
            "outgoing": id_list[7],
            "component": {
                "code": "test",
                "inputs": {
                    "input_test": {"type": "plain", "value": "value1"},
                    "radio_test": {"type": "splice", "value": "before_${global_key1}"},
                },
                "global_outputs": {},
            },
        },
    },
    "flows": {  # 存放该 Pipeline 中所有的线
        id_list[5]: {"id": id_list[5], "source": id_list[1], "target": id_list[3]},
        id_list[6]: {"id": id_list[6], "source": id_list[3], "target": id_list[4]},
        id_list[7]: {"id": id_list[7], "source": id_list[4], "target": id_list[2]},
    },
    "gateways": {},  # 这里存放着网关的详细信息
    "data": {
        "inputs": {
            "${demo_input_test}": {"type": "plain", "value": "value1"},
            "${global_key1}": {"type": "splice", "source_act": id_list[3], "source_key": "key1", "value": ""},
            "${custom_key1}": {"type": "splice", "value": "aaa_${global_key1}"},
            "${custom_key2}": {"type": "plain", "value": "custom2"},
        },
        "outputs": {"${demo_input_test}": "${demo_input_test}", "${global_key1}": "${global_key1}"},
    },
}

WEB_PIPELINE_DATA = {
    "id": id_list[0],
    "name": "name",
    "start_event": {
        "id": id_list[1],
        "name": "start",
        "type": "EmptyStartEvent",
        "incoming": None,
        "outgoing": id_list[5],
    },
    "end_event": {"id": id_list[2], "name": "end", "type": "EmptyEndEvent", "incoming": id_list[7], "outgoing": None},
    "activities": {
        id_list[3]: {
            "id": id_list[3],
            "type": "ServiceActivity",
            "name": "first_task",
            "incoming": id_list[5],
            "outgoing": id_list[6],
            "component": {
                "code": "test",
                "data": {
                    "input_test": {"hook": False, "value": "${custom_key2}"},
                    "radio_test": {"hook": False, "value": "1"},
                },
            },
        },
        id_list[4]: {
            "id": id_list[4],
            "type": "ServiceActivity",
            "name": "first_task",
            "incoming": id_list[6],
            "outgoing": id_list[7],
            "component": {
                "code": "test",
                "data": {
                    "input_test": {"hook": True, "value": "${demo_input_test}"},
                    "radio_test": {"hook": False, "value": "before_${global_key1}"},
                },
            },
        },
    },
    "flows": {  # 存放该 Pipeline 中所有的线
        id_list[5]: {"id": id_list[5], "source": id_list[1], "target": id_list[3]},
        id_list[6]: {"id": id_list[6], "source": id_list[3], "target": id_list[4]},
        id_list[7]: {"id": id_list[7], "source": id_list[4], "target": id_list[2]},
    },
    "gateways": {},  # 这里存放着网关的详细信息
    "constants": {
        "${demo_input_test}": {
            "name": "input",
            "key": "${demo_input_test}",
            "desc": "",
            "validation": "^.*$",
            "show_type": "show",
            "value": "value1",
            "source_type": "component_inputs",
            "source_tag": "demo.input_test",
            # 'source_step': [id_list[4], ],
            "source_info": {id_list[4]: ["input_test"]},
            # 'source_key': '',
            "custom_type": "",
        },
        "${custom_key1}": {
            "name": "input",
            "key": "${custom_key1}",
            "desc": "",
            "validation": "",
            "show_type": "show",
            "value": "aaa_${global_key1}",
            "source_type": "custom",
            "source_tag": "",
            "source_info": {},
            # 'source_key': '',
            "custom_type": "simple_input",
        },
        "${custom_key2}": {
            "name": "input",
            "key": "${custom_key2}",
            "desc": "",
            "validation": "",
            "show_type": "hide",
            "value": "custom2",
            "source_type": "custom",
            "source_tag": "",
            # 'source_step': '',
            # 'source_key': '',
            "custom_type": "simple_input",
        },
        "${global_key1}": {
            "name": "input",
            "key": "${global_key1}",
            "desc": "",
            "validation": "^.*$",
            "show_type": "hide",
            "value": "",
            "source_type": "component_outputs",
            "source_tag": "",
            # 'source_step': id_list[3],
            # 'source_key': 'key1',
            "source_info": {id_list[3]: ["key1"]},
            "custom_type": "",
        },
    },
    "outputs": ["${demo_input_test}", "${global_key1}"],
}

id_list3 = [node_uniqid() for i in range(10)]
sub_pipeline = {
    "id": id_list3[0],
    "name": "name",
    "start_event": {
        "id": id_list3[1],
        "name": "start",
        "type": "EmptyStartEvent",
        "incoming": None,
        "outgoing": id_list3[5],
    },
    "end_event": {"id": id_list3[2], "name": "end", "type": "EmptyEndEvent", "incoming": id_list3[7], "outgoing": None},
    "activities": {
        id_list3[3]: {
            "id": id_list3[3],
            "type": "ServiceActivity",
            "name": "first_task",
            "incoming": id_list3[5],
            "outgoing": id_list3[6],
            "component": {
                "code": "test",
                "inputs": {
                    "input_test": {"type": "plain", "value": "before_after"},
                    "radio_test": {"type": "plain", "value": "1"},
                },
                "global_outputs": {"key1": "${global_key1}"},
            },
        },
        id_list3[4]: {
            "id": id_list3[4],
            "type": "ServiceActivity",
            "name": "first_task",
            "incoming": id_list3[6],
            "outgoing": id_list3[7],
            "component": {
                "code": "test",
                "inputs": {
                    "input_test": {"type": "plain", "value": "value1"},
                    "radio_test": {"type": "splice", "value": "before_${global_key1}"},
                },
                "global_outputs": {},
            },
        },
    },
    "flows": {  # 存放该 Pipeline 中所有的线
        id_list3[5]: {"id": id_list3[5], "source": id_list3[1], "target": id_list3[3]},
        id_list3[6]: {"id": id_list3[6], "source": id_list3[3], "target": id_list3[4]},
        id_list3[7]: {"id": id_list3[7], "source": id_list3[4], "target": id_list3[2]},
    },
    "gateways": {},  # 这里存放着网关的详细信息
    "data": {
        "inputs": {
            "${demo_input_test}": {"type": "plain", "value": "value2"},
            "${global_key1}": {"type": "splice", "source_act": id_list3[3], "source_key": "key1", "value": ""},
            "${custom_key2}": {"type": "splice", "value": "aaa_${global_key1}"},
        },
        "outputs": {"${demo_input_test}": "${demo_input_test_sub}", "${global_key1}": "${global_key1_sub}"},
    },
}

sub_web_pipeline = {
    "id": id_list3[0],
    "name": "name",
    "start_event": {
        "id": id_list3[1],
        "name": "start",
        "type": "EmptyStartEvent",
        "incoming": None,
        "outgoing": id_list3[5],
    },
    "end_event": {"id": id_list3[2], "name": "end", "type": "EmptyEndEvent", "incoming": id_list3[7], "outgoing": None},
    "activities": {
        id_list3[3]: {
            "id": id_list3[3],
            "type": "ServiceActivity",
            "name": "first_task",
            "incoming": id_list3[5],
            "outgoing": id_list3[6],
            "component": {
                "code": "test",
                "data": {
                    "input_test": {"hook": False, "value": "${custom_key2}"},
                    "radio_test": {"hook": False, "value": "1"},
                },
            },
        },
        id_list3[4]: {
            "id": id_list3[4],
            "type": "ServiceActivity",
            "name": "first_task",
            "incoming": id_list3[6],
            "outgoing": id_list3[7],
            "component": {
                "code": "test",
                "data": {
                    "input_test": {"hook": True, "value": "${demo_input_test}"},
                    "radio_test": {"hook": False, "value": "before_${global_key1}_${custom_key2}"},
                },
            },
        },
    },
    "flows": {  # 存放该 Pipeline 中所有的线
        id_list3[5]: {"id": id_list3[5], "source": id_list3[1], "target": id_list3[3]},
        id_list3[6]: {"id": id_list3[6], "source": id_list3[3], "target": id_list3[4]},
        id_list3[7]: {"id": id_list3[7], "source": id_list3[4], "target": id_list3[2]},
    },
    "gateways": {},  # 这里存放着网关的详细信息
    "constants": {
        "${demo_input_test}": {
            "name": "input",
            "key": "${demo_input_test}",
            "desc": "",
            "validation": "^.*$",
            "show_type": "hide",
            "value": "value2",
            "source_type": "component_inputs",
            "source_tag": "demo.input_test",
            # 'source_step': [id_list3[4], ],
            # 'source_key': '',
            "source_info": {id_list3[4]: ["input_test"], id_list3[5]: ["input_test"]},
            "custom_type": "",
        },
        "${custom_key1}": {
            "name": "input",
            "key": "${custom_key1}",
            "desc": "",
            "validation": "",
            "show_type": "hide",
            "value": "aaa_${global_key1}",
            "source_type": "custom",
            "source_tag": "",
            # 'source_step': '',
            # 'source_key': '',
            "source_info": {},
            "custom_type": "simple_input",
        },
        "${custom_key2}": {
            "name": "input",
            "key": "${custom_key2}",
            "desc": "",
            "validation": "",
            "show_type": "hide",
            "value": "custom2",
            "source_type": "custom",
            "source_tag": "",
            # 'source_step': '',
            # 'source_key': '',
            "source_info": {},
            "custom_type": "simple_input",
        },
        "${global_key1}": {
            "name": "input",
            "key": "${global_key1}",
            "desc": "",
            "validation": "^.*$",
            "show_type": "hide",
            "value": "",
            "source_type": "component_outputs",
            "source_tag": "",
            # 'source_step': id_list3[3],
            # 'source_key': 'key1',
            "source_info": {id_list3[3]: ["key1"]},
            "custom_type": "",
        },
    },
    "outputs": ["${demo_input_test}", "${global_key1}"],
}

PIPELINE_WITH_SUB_PROCESS = copy.deepcopy(PIPELINE_DATA)
PIPELINE_WITH_SUB_PROCESS["activities"][id_list[4]] = {
    "id": id_list[4],
    "type": "SubProcess",
    "name": "second_task",
    "incoming": id_list[6],
    "outgoing": id_list[7],
    "pipeline": sub_pipeline,
    "exposed_constants": [],
    "hooked_constants": [],
    "params": {},
}

CONDITIONAL_PARALLEL = {
    "activities": {
        "3adc3e38891233e1b0bf9cdf62dbfd5d": {
            "component": {"code": "test", "global_outputs": {}, "inputs": {}},
            "error_ignorable": False,
            "id": "3adc3e38891233e1b0bf9cdf62dbfd5d",
            "incoming": ["0b5bd2783ba93667b9f197f2fb7a6488"],
            "name": None,
            "optional": False,
            "outgoing": "eb739c39bf6f3394b6db8f6b9220e0c1",
            "type": "ServiceActivity",
        },
        "40b176a1a92d307b9f8a2ec08d2c47ec": {
            "component": {"code": "test", "global_outputs": {}, "inputs": {}},
            "error_ignorable": False,
            "id": "40b176a1a92d307b9f8a2ec08d2c47ec",
            "incoming": ["9395729e7b9d3f1a9396d1dfc3881ab8"],
            "name": None,
            "optional": False,
            "outgoing": "b61b2d9c59ee3243947d337372a99ea7",
            "type": "ServiceActivity",
        },
        "a80da787752f3094a244537788e129b1": {
            "component": {"code": "test", "global_outputs": {}, "inputs": {}},
            "error_ignorable": False,
            "id": "a80da787752f3094a244537788e129b1",
            "incoming": ["6bafc9fd6d6e395aba808725340f15e9"],
            "name": None,
            "optional": False,
            "outgoing": "3f273abe5f3038caa777682b1b62bbde",
            "type": "ServiceActivity",
        },
        "b54bf29c856e36e68b89fb3fe3cabdfd": {
            "component": {"code": "test", "global_outputs": {}, "inputs": {}},
            "error_ignorable": False,
            "id": "b54bf29c856e36e68b89fb3fe3cabdfd",
            "incoming": ["d3f70e28042f3b03ad15e96b69a3f3fc"],
            "name": None,
            "optional": False,
            "outgoing": "33762dce859437f2908129956db280da",
            "type": "ServiceActivity",
        },
        "fd40b66e751733129e854d1e5070c3f1": {
            "component": {"code": "test", "global_outputs": {}, "inputs": {}},
            "error_ignorable": False,
            "id": "fd40b66e751733129e854d1e5070c3f1",
            "incoming": ["a5f1d27c5a873c6ea0a2ec922542f2b0"],
            "name": None,
            "optional": False,
            "outgoing": "b767de1b435a313d8e3da4c111f24fb0",
            "type": "ServiceActivity",
        },
    },
    "data": {"inputs": {}, "outputs": {}},
    "end_event": {
        "id": "60d7c4ec44343e43a89fa12e506641f6",
        "incoming": ["4775f07b91b638b9a705e579955636e4"],
        "name": None,
        "outgoing": "",
        "type": "EmptyEndEvent",
    },
    "flows": {
        "0b5bd2783ba93667b9f197f2fb7a6488": {
            "id": "0b5bd2783ba93667b9f197f2fb7a6488",
            "is_default": False,
            "source": "ea73c396788d37b8beb8df4f79798a09",
            "target": "3adc3e38891233e1b0bf9cdf62dbfd5d",
        },
        "33762dce859437f2908129956db280da": {
            "id": "33762dce859437f2908129956db280da",
            "is_default": False,
            "source": "b54bf29c856e36e68b89fb3fe3cabdfd",
            "target": "757fcd23b18238bfa570993f0429d0d3",
        },
        "3f273abe5f3038caa777682b1b62bbde": {
            "id": "3f273abe5f3038caa777682b1b62bbde",
            "is_default": False,
            "source": "a80da787752f3094a244537788e129b1",
            "target": "757fcd23b18238bfa570993f0429d0d3",
        },
        "4775f07b91b638b9a705e579955636e4": {
            "id": "4775f07b91b638b9a705e579955636e4",
            "is_default": False,
            "source": "757fcd23b18238bfa570993f0429d0d3",
            "target": "60d7c4ec44343e43a89fa12e506641f6",
        },
        "6bafc9fd6d6e395aba808725340f15e9": {
            "id": "6bafc9fd6d6e395aba808725340f15e9",
            "is_default": False,
            "source": "ea73c396788d37b8beb8df4f79798a09",
            "target": "a80da787752f3094a244537788e129b1",
        },
        "739716dfe0353ce8a590408d6452165e": {
            "id": "739716dfe0353ce8a590408d6452165e",
            "is_default": False,
            "source": "ebe56dd469a93067983ea847e2b61978",
            "target": "ea73c396788d37b8beb8df4f79798a09",
        },
        "9395729e7b9d3f1a9396d1dfc3881ab8": {
            "id": "9395729e7b9d3f1a9396d1dfc3881ab8",
            "is_default": False,
            "source": "ea73c396788d37b8beb8df4f79798a09",
            "target": "40b176a1a92d307b9f8a2ec08d2c47ec",
        },
        "a5f1d27c5a873c6ea0a2ec922542f2b0": {
            "id": "a5f1d27c5a873c6ea0a2ec922542f2b0",
            "is_default": False,
            "source": "ea73c396788d37b8beb8df4f79798a09",
            "target": "fd40b66e751733129e854d1e5070c3f1",
        },
        "b61b2d9c59ee3243947d337372a99ea7": {
            "id": "b61b2d9c59ee3243947d337372a99ea7",
            "is_default": False,
            "source": "40b176a1a92d307b9f8a2ec08d2c47ec",
            "target": "757fcd23b18238bfa570993f0429d0d3",
        },
        "b767de1b435a313d8e3da4c111f24fb0": {
            "id": "b767de1b435a313d8e3da4c111f24fb0",
            "is_default": False,
            "source": "fd40b66e751733129e854d1e5070c3f1",
            "target": "757fcd23b18238bfa570993f0429d0d3",
        },
        "d3f70e28042f3b03ad15e96b69a3f3fc": {
            "id": "d3f70e28042f3b03ad15e96b69a3f3fc",
            "is_default": False,
            "source": "ea73c396788d37b8beb8df4f79798a09",
            "target": "b54bf29c856e36e68b89fb3fe3cabdfd",
        },
        "eb739c39bf6f3394b6db8f6b9220e0c1": {
            "id": "eb739c39bf6f3394b6db8f6b9220e0c1",
            "is_default": False,
            "source": "3adc3e38891233e1b0bf9cdf62dbfd5d",
            "target": "757fcd23b18238bfa570993f0429d0d3",
        },
    },
    "gateways": {
        "757fcd23b18238bfa570993f0429d0d3": {
            "id": "757fcd23b18238bfa570993f0429d0d3",
            "incoming": [
                "b61b2d9c59ee3243947d337372a99ea7",
                "eb739c39bf6f3394b6db8f6b9220e0c1",
                "33762dce859437f2908129956db280da",
                "b767de1b435a313d8e3da4c111f24fb0",
                "3f273abe5f3038caa777682b1b62bbde",
            ],
            "name": None,
            "outgoing": "4775f07b91b638b9a705e579955636e4",
            "type": "ConvergeGateway",
        },
        "ea73c396788d37b8beb8df4f79798a09": {
            "conditions": {
                "0b5bd2783ba93667b9f197f2fb7a6488": {"evaluate": "True == True"},
                "6bafc9fd6d6e395aba808725340f15e9": {"evaluate": "True == False"},
                "9395729e7b9d3f1a9396d1dfc3881ab8": {"evaluate": "True == True"},
                "a5f1d27c5a873c6ea0a2ec922542f2b0": {"evaluate": "True == False"},
                "d3f70e28042f3b03ad15e96b69a3f3fc": {"evaluate": "True == False"},
            },
            "id": "ea73c396788d37b8beb8df4f79798a09",
            "incoming": ["739716dfe0353ce8a590408d6452165e"],
            "name": None,
            "outgoing": [
                "9395729e7b9d3f1a9396d1dfc3881ab8",
                "0b5bd2783ba93667b9f197f2fb7a6488",
                "d3f70e28042f3b03ad15e96b69a3f3fc",
                "a5f1d27c5a873c6ea0a2ec922542f2b0",
                "6bafc9fd6d6e395aba808725340f15e9",
            ],
            "type": "ConditionalParallelGateway",
        },
    },
    "id": "28b3413186dd3cd48310531354bc897a",
    "start_event": {
        "id": "ebe56dd469a93067983ea847e2b61978",
        "incoming": "",
        "name": None,
        "outgoing": "739716dfe0353ce8a590408d6452165e",
        "type": "EmptyStartEvent",
    },
}
