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
}

# 子流程 全局输入全部hide 输出全部无引用到父流程
WEB_PIPELINE_WITH_SUB_PROCESS = copy.deepcopy(WEB_PIPELINE_DATA)
WEB_PIPELINE_WITH_SUB_PROCESS["activities"][id_list[4]] = {
    "id": id_list[4],
    "type": "SubProcess",
    "name": "second_task",
    "incoming": id_list[6],
    "outgoing": id_list[7],
    "pipeline": sub_web_pipeline,
    "hooked_constants": [],
}

# 子流程 全局输入部分show，并且引用了父流程的全局变量，无引用到父流程 输出全部无引用到父流程
id_list2 = [node_uniqid() for i in range(20)]
sub_web_pipeline2 = {
    "id": id_list2[0],
    "name": "name",
    "start_event": {
        "id": id_list2[1],
        "name": "start",
        "type": "EmptyStartEvent",
        "incoming": None,
        "outgoing": id_list2[5],
    },
    "end_event": {"id": id_list2[2], "name": "end", "type": "EmptyEndEvent", "incoming": id_list2[7], "outgoing": None},
    "activities": {
        id_list2[3]: {
            "id": id_list2[3],
            "type": "ServiceActivity",
            "name": "first_task",
            "incoming": id_list2[5],
            "outgoing": id_list2[6],
            "component": {
                "code": "test",
                "data": {
                    "input_test": {"hook": False, "value": "${custom_key2}"},
                    "radio_test": {"hook": False, "value": "1"},
                },
            },
        },
        id_list2[4]: {
            "id": id_list2[4],
            "type": "ServiceActivity",
            "name": "first_task",
            "incoming": id_list2[6],
            "outgoing": id_list2[7],
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
        id_list2[5]: {"id": id_list2[5], "source": id_list2[1], "target": id_list2[3]},
        id_list2[6]: {"id": id_list2[6], "source": id_list2[3], "target": id_list2[4]},
        id_list2[7]: {"id": id_list2[7], "source": id_list2[4], "target": id_list2[2]},
    },
    "gateways": {},  # 这里存放着网关的详细信息
    "constants": {
        "${demo_input_test}": {
            "name": "input",
            "key": "${demo_input_test}",
            "desc": "",
            "validation": "^.*$",
            "show_type": "show",
            "value": "value2_${root_key1}",
            "source_type": "component_inputs",
            "source_tag": "demo.input_test",
            # 'source_step': [id_list2[4], ],
            # 'source_key': '',
            "source_info": {id_list2[4]: ["input_test"]},
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
            # 'source_step': id_list2[3],
            # 'source_key': 'key1',
            "source_info": {id_list2[3]: ["key1"]},
            "custom_type": "",
        },
    },
    "outputs": ["${demo_input_test}", "${global_key1}"],
}

WEB_PIPELINE_WITH_SUB_PROCESS2 = {
    "id": id_list2[15],
    "name": "web_pipeline3",
    "start_event": {
        "id": id_list2[8],
        "name": "start",
        "type": "EmptyStartEvent",
        "incoming": None,
        "outgoing": id_list2[12],
    },
    "end_event": {
        "id": id_list2[11],
        "name": "end",
        "type": "EmptyEndEvent",
        "incoming": id_list2[14],
        "outgoing": None,
    },
    "activities": {
        id_list2[9]: {
            "id": id_list2[9],
            "type": "ServiceActivity",
            "name": "act_task",
            "incoming": id_list2[12],
            "outgoing": id_list2[13],
            "component": {
                "code": "test",
                "data": {"input_test": {"hook": False, "value": "test1"}, "radio_test": {"hook": False, "value": "1"}},
            },
        },
        id_list2[10]: {
            "id": id_list2[10],
            "type": "SubProcess",
            "name": "sub_pipeline",
            "incoming": id_list2[13],
            "outgoing": id_list2[14],
            "pipeline": sub_web_pipeline2,
            "hooked_constants": [],
        },
    },
    "flows": {
        id_list2[12]: {"id": id_list2[12], "source": id_list2[8], "target": id_list2[9]},
        id_list2[13]: {"id": id_list2[13], "source": id_list2[9], "target": id_list2[10]},
        id_list2[14]: {"id": id_list2[14], "source": id_list2[10], "target": id_list2[11]},
    },
    "gateways": {},
    "constants": {
        "${root_key1}": {
            "name": "root_key1",
            "key": "${root_key1}",
            "desc": "",
            "validation": "",
            "show_type": "hide",
            "value": "aaa_${root_key2}",
            "source_type": "custom",
            "source_tag": "",
            # 'source_step': '',
            # 'source_key': '',
            "source_info": {},
            "custom_type": "simple_input",
        },
        "${root_key2}": {
            "name": "root_key2",
            "key": "${root_key2}",
            "desc": "",
            "validation": "",
            "show_type": "show",
            "value": "root_value2",
            "source_type": "custom",
            "source_tag": "",
            # 'source_step': '',
            # 'source_key': '',
            "source_info": {},
            "custom_type": "simple_input",
        },
    },
    "outputs": [],
}

# 子流程 全局输入部分show，部分引用到父流程 全部输出无引用到父流程
WEB_PIPELINE_WITH_SUB_PROCESS3 = {
    "id": node_uniqid(),
    "activities": {
        "a69a41785c7b30afbd46c532a6f466a7": {
            "outgoing": "ca1aab540d4c35f5a2f60a05ed80181d",
            "incoming": "199fda538c9e39d3876465f8925774f2",
            "name": "\u8282\u70b9_1",
            "optional": False,
            "pipeline": {
                "activities": {
                    "8f7428b073963641bcf8ce01b447e17d": {
                        "outgoing": "d5bafd9b95d739a892ded011e70708ac",
                        "incoming": "fd2c65c4b4e7313abf8fb26ddb6b406b",
                        "name": "\u8282\u70b9_1",
                        "type": "ServiceActivity",
                        "component": {
                            "code": "test",
                            "data": {
                                "input_test": {"hook": True, "is_valid": True, "value": "${input_test}"},
                                "radio_test": {"hook": False, "is_valid": True, "value": "1"},
                            },
                        },
                        "ignore": False,
                        "optional": False,
                        "id": "8f7428b073963641bcf8ce01b447e17d",
                        "loop": None,
                    }
                },
                "end_event": {
                    "incoming": "d5bafd9b95d739a892ded011e70708ac",
                    "outgoing": "",
                    "type": "EmptyEndEvent",
                    "id": "4a93549e80c83bd293d4c4be658cb99f",
                    "name": "",
                },
                "outputs": [],
                "flows": {
                    "fd2c65c4b4e7313abf8fb26ddb6b406b": {
                        "is_default": False,
                        "source": "b3a6c3e168c83d6a951b962935ebc10e",
                        "id": "fd2c65c4b4e7313abf8fb26ddb6b406b",
                        "target": "8f7428b073963641bcf8ce01b447e17d",
                    },
                    "d5bafd9b95d739a892ded011e70708ac": {
                        "is_default": False,
                        "source": "8f7428b073963641bcf8ce01b447e17d",
                        "id": "d5bafd9b95d739a892ded011e70708ac",
                        "target": "4a93549e80c83bd293d4c4be658cb99f",
                    },
                },
                "start_event": {
                    "incoming": "",
                    "outgoing": "fd2c65c4b4e7313abf8fb26ddb6b406b",
                    "type": "EmptyStartEvent",
                    "id": "b3a6c3e168c83d6a951b962935ebc10e",
                    "name": "",
                },
                "id": "a69a41785c7b30afbd46c532a6f466a7",
                "constants": {
                    "${input_test}": {
                        "source_tag": "demo.input_test",
                        "name": "\u8f93\u5165\u6846",
                        "custom_type": "input",
                        # u'source_key': u'',
                        "value": "${input_test}",
                        "show_type": "show",
                        "source_type": "component_inputs",
                        "is_valid": True,
                        "key": "${input_test}",
                        "desc": "",
                        "validation": "^.*$",
                        # u'source_step': [u'8f7428b073963641bcf8ce01b447e17d'],
                        "source_info": {"8f7428b073963641bcf8ce01b447e17d": ["input_test"]},
                    }
                },
                "gateways": {},
            },
            "id": "a69a41785c7b30afbd46c532a6f466a7",
            "ignore": False,
            "type": "SubProcess",
            "template_id": "dd210a6ecf0e374985ed87bcc087d447",
            "loop": None,
            "hooked_constants": ["${input_test}"],
        }
    },
    "end_event": {
        "type": "EmptyEndEvent",
        "outgoing": "",
        "incoming": "ca1aab540d4c35f5a2f60a05ed80181d",
        "id": "e02925dc56c7354faf5b55c4b8afe691",
        "name": "",
    },
    "outputs": [],
    "flows": {
        "ca1aab540d4c35f5a2f60a05ed80181d": {
            "is_default": False,
            "source": "a69a41785c7b30afbd46c532a6f466a7",
            "id": "ca1aab540d4c35f5a2f60a05ed80181d",
            "target": "e02925dc56c7354faf5b55c4b8afe691",
        },
        "199fda538c9e39d3876465f8925774f2": {
            "is_default": False,
            "source": "48a815abbadf3845ac5283036c064a9a",
            "id": "199fda538c9e39d3876465f8925774f2",
            "target": "a69a41785c7b30afbd46c532a6f466a7",
        },
    },
    "start_event": {
        "type": "EmptyStartEvent",
        "outgoing": "199fda538c9e39d3876465f8925774f2",
        "incoming": "",
        "id": "48a815abbadf3845ac5283036c064a9a",
        "name": "",
    },
    "constants": {
        "${input_test}": {
            "source_tag": "demo.input_test",
            "name": "\u8f93\u5165\u6846",
            "custom_type": "input",
            # u'source_key': u'',
            "value": "1",
            "show_type": "show",
            "source_type": "component_inputs",
            "key": "${input_test}",
            "desc": "",
            "validation": "^.*$",
            # u'source_step': [u'a69a41785c7b30afbd46c532a6f466a7'],
            "source_info": {"8f7428b073963641bcf8ce01b447e17d": ["input_test"]},
        }
    },
    "gateways": {},
}
# 子流程 全局输入部分show，并且引用了父流程的全局变量，无引用到父流程 输出全部无引用到父流程

# 子流程 全局输入部分show，并且引用到父流程 输出全部无引用到父流程
