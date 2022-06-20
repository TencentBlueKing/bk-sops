# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from pipeline.utils.uniqid import node_uniqid

TEST_PROJECT_ID = "2"  # do not change this to non number
TEST_ID_LIST = [node_uniqid() for i in range(10)]
TEST_PIPELINE_TREE = {
    "id": TEST_ID_LIST[0],
    "name": "name",
    "start_event": {
        "id": TEST_ID_LIST[1],
        "name": "start",
        "type": "EmptyStartEvent",
        "incoming": None,
        "outgoing": TEST_ID_LIST[5],
    },
    "end_event": {
        "id": TEST_ID_LIST[2],
        "name": "end",
        "type": "EmptyEndEvent",
        "incoming": TEST_ID_LIST[7],
        "outgoing": None,
    },
    "activities": {
        TEST_ID_LIST[3]: {
            "id": TEST_ID_LIST[3],
            "type": "ServiceActivity",
            "name": "first_task",
            "incoming": TEST_ID_LIST[5],
            "outgoing": TEST_ID_LIST[6],
            "optional": True,
            "component": {
                "code": "test",
                "data": {
                    "input_test": {"hook": False, "value": "${custom_key1}"},
                    "radio_test": {"hook": False, "value": "1"},
                },
            },
        },
        TEST_ID_LIST[4]: {
            "id": TEST_ID_LIST[4],
            "type": "ServiceActivity",
            "name": "first_task",
            "incoming": TEST_ID_LIST[6],
            "outgoing": TEST_ID_LIST[7],
            "optional": True,
            "component": {
                "code": "test",
                "data": {
                    "input_test": {"hook": True, "value": "${custom_key2}"},
                    "radio_test": {"hook": False, "value": "2"},
                },
            },
        },
        TEST_ID_LIST[5]: {
            "id": TEST_ID_LIST[5],
            "template_id": TEST_ID_LIST[5],
            "type": "SubProcess",
            "name": "subproc 1",
            "pipeline": {
                "activities": {
                    "9": {
                        "type": "ServiceActivity",
                        "id": "9",
                        "name": "act_9",
                        "component": {"code": "bk_notify", "data": {}, "version": "legacy"},
                    },
                    "10": {
                        "type": "ServiceActivity",
                        "id": "10",
                        "name": "act_10",
                        "component": {"code": "bk_notify", "data": {}, "version": "v1.0"},
                    },
                    "11": {  # node without version
                        "type": "ServiceActivity",
                        "id": "11",
                        "name": "act_11",
                        "component": {"code": "bk_job", "data": {}},
                    },
                },
                "constants": {},
            },
        },
    },
    "flows": {  # 存放该 Pipeline 中所有的线
        TEST_ID_LIST[5]: {"id": TEST_ID_LIST[5], "source": TEST_ID_LIST[1], "target": TEST_ID_LIST[3]},
        TEST_ID_LIST[6]: {"id": TEST_ID_LIST[6], "source": TEST_ID_LIST[3], "target": TEST_ID_LIST[4]},
        TEST_ID_LIST[7]: {"id": TEST_ID_LIST[7], "source": TEST_ID_LIST[4], "target": TEST_ID_LIST[2]},
    },
    "gateways": {},  # 这里存放着网关的详细信息
    "constants": {
        "${custom_key1}": {
            "index": 0,
            "name": "input1",
            "key": "${custom_key1}",
            "desc": "",
            "validation": "^.*$",
            "show_type": "show",
            "value": "value1",
            "source_type": "custom",
            "source_tag": "",
            "source_info": {},
            "custom_type": "input",
        },
        "${custom_key2}": {
            "index": 1,
            "name": "input2",
            "key": "${custom_key2}",
            "desc": "",
            "validation": "^.*$",
            "show_type": "show",
            "value": "value1",
            "source_type": "custom",
            "source_tag": "",
            "source_info": {},
            "custom_type": "input",
        },
    },
    "outputs": ["${custom_key1}"],
}

TEST_STATUS_TREE = {
    "result": True,
    "data": {
        "id": "n72bdcdac7a635f8b584ab8c660483f7",
        "state": "FINISHED",
        "root_id:": "n72bdcdac7a635f8b584ab8c660483f7",
        "parent_id": "n72bdcdac7a635f8b584ab8c660483f7",
        "version": "v538710591dae473bbe3f02f9c8fb2b2f",
        "loop": 1,
        "retry": 0,
        "skip": False,
        "error_ignorable": False,
        "error_ignored": False,
        "children": {
            "nf0bc104bec93e9681cfaec459a2323f": {
                "id": "nf0bc104bec93e9681cfaec459a2323f",
                "state": "FINISHED",
                "root_id:": "n72bdcdac7a635f8b584ab8c660483f7",
                "parent_id": "n72bdcdac7a635f8b584ab8c660483f7",
                "version": "v2cf10a5ca7ce438f884c89cdf5410ae7",
                "loop": 1,
                "retry": 0,
                "skip": False,
                "error_ignorable": False,
                "error_ignored": False,
                "children": {},
                "elapsed_time": 0,
                "start_time": "2021-09-15 18:27:39 +0800",
                "finish_time": "2021-09-15 18:27:39 +0800",
            },
            "n7b6987cd4563f12a150ab0268d1e537": {
                "id": "n7b6987cd4563f12a150ab0268d1e537",
                "state": "FINISHED",
                "root_id:": "n72bdcdac7a635f8b584ab8c660483f7",
                "parent_id": "n72bdcdac7a635f8b584ab8c660483f7",
                "version": "va78ecde5cd16412095e7a4f618a35ed5",
                "loop": 1,
                "retry": 0,
                "skip": False,
                "error_ignorable": False,
                "error_ignored": False,
                "children": {},
                "elapsed_time": 0,
                "start_time": "2021-09-15 18:27:39 +0800",
                "finish_time": "2021-09-15 18:27:39 +0800",
            },
            "nef298d10e6837e5a8a0124c4269a378": {
                "id": "nef298d10e6837e5a8a0124c4269a378",
                "state": "FINISHED",
                "root_id:": "n72bdcdac7a635f8b584ab8c660483f7",
                "parent_id": "n72bdcdac7a635f8b584ab8c660483f7",
                "version": "v62c3aa08cdaa4128886c97c57751ade4",
                "loop": 1,
                "retry": 0,
                "skip": False,
                "error_ignorable": False,
                "error_ignored": False,
                "children": {},
                "elapsed_time": 0,
                "start_time": "2021-09-15 18:27:39 +0800",
                "finish_time": "2021-09-15 18:27:39 +0800",
            },
            "n23e0402c2e83c54bfdefa0a4d05c8fa": {
                "id": "n23e0402c2e83c54bfdefa0a4d05c8fa",
                "state": "FINISHED",
                "root_id:": "n72bdcdac7a635f8b584ab8c660483f7",
                "parent_id": "n72bdcdac7a635f8b584ab8c660483f7",
                "version": "v9024072ec8034791b34602144b9812cb",
                "loop": 1,
                "retry": 0,
                "skip": False,
                "error_ignorable": False,
                "error_ignored": False,
                "children": {},
                "elapsed_time": 0,
                "start_time": "2021-09-15 18:27:39 +0800",
                "finish_time": "2021-09-15 18:27:39 +0800",
            },
        },
        "elapsed_time": 0,
        "start_time": "2021-09-15 18:27:39 +0800",
        "finish_time": "2021-09-15 18:27:39 +0800",
    },
    "code": 0,
    "message": "",
}

TEST_EXECUTION_DATA = {
    "activities": {
        "n6f79bc0359731438dbb7373ba86b96c": {
            "component": {
                "code": "sleep_timer",
                "data": {"bk_timing": {"hook": False, "value": "1"}, "force_check": {"hook": False, "value": True}},
                "version": "legacy",
            },
            "error_ignorable": False,
            "id": "n6f79bc0359731438dbb7373ba86b96c",
            "incoming": ["l67b95cd84bd35f7b0cf3a904533e8d2"],
            "loop": None,
            "name": "定时",
            "optional": True,
            "outgoing": "le574477746d36a1b4a602640ead5d4d",
            "stage_name": "",
            "type": "ServiceActivity",
            "retryable": True,
            "skippable": True,
        },
        "ncc95471ca323ed9885d4015550d5fcd": {
            "component": {
                "code": "sleep_timer",
                "data": {"bk_timing": {"hook": False, "value": "1"}, "force_check": {"hook": False, "value": True}},
                "version": "legacy",
            },
            "error_ignorable": False,
            "id": "ncc95471ca323ed9885d4015550d5fcd",
            "incoming": ["le574477746d36a1b4a602640ead5d4d"],
            "loop": None,
            "name": "定时",
            "optional": True,
            "outgoing": "l5b8b115cddd3ed4b498783b133e695c",
            "stage_name": "",
            "type": "ServiceActivity",
            "retryable": True,
            "skippable": True,
        },
    },
    "constants": {},
    "end_event": {
        "id": "n969852b026e3878bf2409821c3b0beb",
        "incoming": ["l5b8b115cddd3ed4b498783b133e695c"],
        "name": "",
        "outgoing": "",
        "type": "EmptyEndEvent",
    },
    "flows": {
        "l67b95cd84bd35f7b0cf3a904533e8d2": {
            "id": "l67b95cd84bd35f7b0cf3a904533e8d2",
            "is_default": False,
            "source": "n4ec6863a96a3f86b8cf397957624ab2",
            "target": "n6f79bc0359731438dbb7373ba86b96c",
        },
        "le574477746d36a1b4a602640ead5d4d": {
            "id": "le574477746d36a1b4a602640ead5d4d",
            "is_default": False,
            "source": "n6f79bc0359731438dbb7373ba86b96c",
            "target": "ncc95471ca323ed9885d4015550d5fcd",
        },
        "l5b8b115cddd3ed4b498783b133e695c": {
            "id": "l5b8b115cddd3ed4b498783b133e695c",
            "is_default": False,
            "source": "ncc95471ca323ed9885d4015550d5fcd",
            "target": "n969852b026e3878bf2409821c3b0beb",
        },
    },
    "gateways": {},
    "line": [
        {
            "id": "l67b95cd84bd35f7b0cf3a904533e8d2",
            "source": {"arrow": "Right", "id": "n4ec6863a96a3f86b8cf397957624ab2"},
            "target": {"arrow": "Left", "id": "n6f79bc0359731438dbb7373ba86b96c"},
        },
        {
            "source": {"id": "n6f79bc0359731438dbb7373ba86b96c", "arrow": "Right"},
            "target": {"id": "ncc95471ca323ed9885d4015550d5fcd", "arrow": "Left"},
            "id": "le574477746d36a1b4a602640ead5d4d",
        },
        {
            "source": {"id": "ncc95471ca323ed9885d4015550d5fcd", "arrow": "Right"},
            "target": {"id": "n969852b026e3878bf2409821c3b0beb", "arrow": "Left"},
            "id": "l5b8b115cddd3ed4b498783b133e695c",
        },
    ],
    "location": [
        {"id": "n4ec6863a96a3f86b8cf397957624ab2", "type": "startpoint", "x": 40, "y": 150},
        {
            "id": "n6f79bc0359731438dbb7373ba86b96c",
            "type": "tasknode",
            "name": "定时",
            "stage_name": "",
            "x": 165,
            "y": 160,
            "group": "蓝鲸服务(BK)",
            "icon": "",
        },
        {"id": "n969852b026e3878bf2409821c3b0beb", "type": "endpoint", "x": 710, "y": 150},
        {
            "id": "ncc95471ca323ed9885d4015550d5fcd",
            "type": "tasknode",
            "name": "定时",
            "stage_name": "",
            "x": 355,
            "y": 169,
            "group": "蓝鲸服务(BK)",
            "icon": "",
        },
    ],
    "outputs": [],
    "start_event": {
        "id": "n4ec6863a96a3f86b8cf397957624ab2",
        "incoming": "",
        "name": "",
        "outgoing": "l67b95cd84bd35f7b0cf3a904533e8d2",
        "type": "EmptyStartEvent",
    },
    "id": "n1679a85112b361e8085d8bcb780da50",
}
