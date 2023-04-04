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

from django.test import TestCase

from gcloud.tasktmpl3.domains.constants import get_task_referenced_constants


class PreviewTaskReferencedConstantsTestCase(TestCase):
    def setUp(self):
        self.maxDiff = None
        self.pipeline_tree = {
            "activities": {
                "node79c1a6173a292ce85d134781092a": {
                    "component": {
                        "code": "bk_display",
                        "data": {"bk_display_message": {"hook": False, "need_render": True, "value": "${a}"}},
                        "version": "1.0",
                    },
                    "error_ignorable": False,
                    "id": "node79c1a6173a292ce85d134781092a",
                    "incoming": ["line213fe156e33362bf2c167b499e96"],
                    "loop": None,
                    "name": "消息展示",
                    "optional": True,
                    "outgoing": "linea6d8321c0a9b22b3c761f1c36f41",
                    "stage_name": "",
                    "type": "ServiceActivity",
                    "retryable": True,
                    "skippable": True,
                    "auto_retry": {"enable": False, "interval": 0, "times": 1},
                    "timeout_config": {"enable": False, "seconds": 10, "action": "forced_fail"},
                    "labels": [],
                },
                "nodef70519ccb22cef0575f22eec55c0": {
                    "component": {
                        "code": "bk_display",
                        "data": {
                            "bk_display_message": {"hook": True, "need_render": True, "value": "${bk_display_message}"}
                        },
                        "version": "1.0",
                    },
                    "error_ignorable": False,
                    "id": "nodef70519ccb22cef0575f22eec55c0",
                    "incoming": ["line5e97e7c2dc60f9008c79c2ac02c5"],
                    "loop": None,
                    "name": "消息展示",
                    "optional": True,
                    "outgoing": "line92bd5be9e3eaa50e38534d98b7d3",
                    "stage_name": "",
                    "type": "ServiceActivity",
                    "retryable": True,
                    "skippable": True,
                    "auto_retry": {"enable": False, "interval": 0, "times": 1},
                    "timeout_config": {"enable": False, "seconds": 10, "action": "forced_fail"},
                    "labels": [],
                },
                "node1a3fd48fa81f31db0cf2c13be697": {
                    "component": {
                        "code": "bk_display",
                        "data": {"bk_display_message": {"hook": False, "need_render": True, "value": "${c}"}},
                        "version": "1.0",
                    },
                    "error_ignorable": False,
                    "id": "node1a3fd48fa81f31db0cf2c13be697",
                    "incoming": ["line5a17d3b8cea6c14266d43f9446a6"],
                    "loop": None,
                    "name": "消息展示",
                    "optional": True,
                    "outgoing": "linee6e92c3334ef12f91e51877a3d86",
                    "stage_name": "",
                    "type": "ServiceActivity",
                    "retryable": True,
                    "skippable": True,
                    "auto_retry": {"enable": False, "interval": 0, "times": 1},
                    "timeout_config": {"enable": False, "seconds": 10, "action": "forced_fail"},
                    "labels": [],
                },
                "noded72838198dfc052149b5b1cd394b": {
                    "component": {
                        "code": "bk_display",
                        "data": {"bk_display_message": {"hook": False, "need_render": True, "value": "${a} ${c}"}},
                        "version": "1.0",
                    },
                    "error_ignorable": False,
                    "id": "noded72838198dfc052149b5b1cd394b",
                    "incoming": ["linee6e92c3334ef12f91e51877a3d86"],
                    "loop": None,
                    "name": "消息展示",
                    "optional": True,
                    "outgoing": "line6057bece09e3e21a6c89b78f9104",
                    "stage_name": "",
                    "type": "ServiceActivity",
                    "retryable": True,
                    "skippable": True,
                    "auto_retry": {"enable": False, "interval": 0, "times": 1},
                    "timeout_config": {"enable": False, "seconds": 10, "action": "forced_fail"},
                    "labels": [],
                },
            },
            "constants": {
                "${bk_display_message}": {
                    "name": "展示内容",
                    "key": "${bk_display_message}",
                    "desc": "",
                    "custom_type": "",
                    "source_info": {"nodef70519ccb22cef0575f22eec55c0": ["bk_display_message"]},
                    "source_tag": "bk_display.bk_display_message",
                    "value": "${a}",
                    "show_type": "show",
                    "source_type": "component_inputs",
                    "validation": "",
                    "index": 0,
                    "version": "1.0",
                    "form_schema": {"type": "textarea", "attrs": {"name": "展示内容", "hookable": True}},
                    "plugin_code": "",
                },
                "${a}": {
                    "custom_type": "input",
                    "desc": "",
                    "form_schema": {"type": "input", "attrs": {"name": "输入框", "hookable": True, "validation": []}},
                    "index": 1,
                    "key": "${a}",
                    "name": "a",
                    "show_type": "show",
                    "source_info": {},
                    "source_tag": "input.input",
                    "source_type": "custom",
                    "validation": "^.+$",
                    "is_condition_hide": "false",
                    "pre_render_mako": False,
                    "value": "a",
                    "version": "legacy",
                },
                "${b}": {
                    "custom_type": "input",
                    "desc": "",
                    "form_schema": {"type": "input", "attrs": {"name": "输入框", "hookable": True, "validation": []}},
                    "index": 2,
                    "key": "${b}",
                    "name": "b",
                    "show_type": "show",
                    "source_info": {},
                    "source_tag": "input.input",
                    "source_type": "custom",
                    "validation": "^.+$",
                    "is_condition_hide": "false",
                    "pre_render_mako": False,
                    "value": "2",
                    "version": "legacy",
                },
                "${c}": {
                    "custom_type": "input",
                    "desc": "",
                    "form_schema": {"type": "input", "attrs": {"name": "输入框", "hookable": True, "validation": []}},
                    "index": 3,
                    "key": "${c}",
                    "name": "c",
                    "show_type": "show",
                    "source_info": {},
                    "source_tag": "input.input",
                    "source_type": "custom",
                    "validation": "^.+$",
                    "is_condition_hide": "false",
                    "pre_render_mako": False,
                    "value": "c",
                    "version": "legacy",
                },
            },
            "end_event": {
                "id": "node922b2d2223e529643a48f530ee62",
                "incoming": ["line6057bece09e3e21a6c89b78f9104", "line92bd5be9e3eaa50e38534d98b7d3"],
                "name": "",
                "outgoing": "",
                "type": "EmptyEndEvent",
                "labels": [],
            },
            "flows": {
                "line213fe156e33362bf2c167b499e96": {
                    "id": "line213fe156e33362bf2c167b499e96",
                    "is_default": False,
                    "source": "node04f13d4060e03d5a9baee9aee139",
                    "target": "node79c1a6173a292ce85d134781092a",
                },
                "line5e97e7c2dc60f9008c79c2ac02c5": {
                    "id": "line5e97e7c2dc60f9008c79c2ac02c5",
                    "is_default": False,
                    "source": "node1595e1f3508485c50f874c282c24",
                    "target": "nodef70519ccb22cef0575f22eec55c0",
                },
                "line5a17d3b8cea6c14266d43f9446a6": {
                    "id": "line5a17d3b8cea6c14266d43f9446a6",
                    "is_default": False,
                    "source": "node1595e1f3508485c50f874c282c24",
                    "target": "node1a3fd48fa81f31db0cf2c13be697",
                },
                "linea6d8321c0a9b22b3c761f1c36f41": {
                    "id": "linea6d8321c0a9b22b3c761f1c36f41",
                    "is_default": False,
                    "source": "node79c1a6173a292ce85d134781092a",
                    "target": "node1595e1f3508485c50f874c282c24",
                },
                "linee6e92c3334ef12f91e51877a3d86": {
                    "id": "linee6e92c3334ef12f91e51877a3d86",
                    "is_default": False,
                    "source": "node1a3fd48fa81f31db0cf2c13be697",
                    "target": "noded72838198dfc052149b5b1cd394b",
                },
                "line6057bece09e3e21a6c89b78f9104": {
                    "id": "line6057bece09e3e21a6c89b78f9104",
                    "is_default": False,
                    "source": "noded72838198dfc052149b5b1cd394b",
                    "target": "node922b2d2223e529643a48f530ee62",
                },
                "line92bd5be9e3eaa50e38534d98b7d3": {
                    "id": "line92bd5be9e3eaa50e38534d98b7d3",
                    "is_default": False,
                    "source": "nodef70519ccb22cef0575f22eec55c0",
                    "target": "node922b2d2223e529643a48f530ee62",
                },
            },
            "gateways": {
                "node1595e1f3508485c50f874c282c24": {
                    "id": "node1595e1f3508485c50f874c282c24",
                    "incoming": ["linea6d8321c0a9b22b3c761f1c36f41"],
                    "name": "",
                    "outgoing": ["line5e97e7c2dc60f9008c79c2ac02c5", "line5a17d3b8cea6c14266d43f9446a6"],
                    "type": "ExclusiveGateway",
                    "conditions": {
                        "line5e97e7c2dc60f9008c79c2ac02c5": {
                            "evaluate": '"${b}" == "1"',
                            "name": "条件1",
                            "tag": "branch_node1595e1f3508485c50f874c282c24_nodef70519ccb22cef0575f22eec55c0",
                        },
                        "line5a17d3b8cea6c14266d43f9446a6": {
                            "evaluate": '"${b}" == "2"',
                            "name": "条件2",
                            "tag": "branch_node1595e1f3508485c50f874c282c24_node1a3fd48fa81f31db0cf2c13be697",
                        },
                    },
                    "labels": [],
                }
            },
            "line": [
                {
                    "id": "line213fe156e33362bf2c167b499e96",
                    "source": {"arrow": "Right", "id": "node04f13d4060e03d5a9baee9aee139"},
                    "target": {"arrow": "Left", "id": "node79c1a6173a292ce85d134781092a"},
                },
                {
                    "id": "line5e97e7c2dc60f9008c79c2ac02c5",
                    "source": {"arrow": "Right", "id": "node1595e1f3508485c50f874c282c24"},
                    "target": {"arrow": "Left", "id": "nodef70519ccb22cef0575f22eec55c0"},
                },
                {
                    "id": "line5a17d3b8cea6c14266d43f9446a6",
                    "source": {"arrow": "Bottom", "id": "node1595e1f3508485c50f874c282c24"},
                    "target": {"arrow": "Left", "id": "node1a3fd48fa81f31db0cf2c13be697"},
                },
                {
                    "id": "linea6d8321c0a9b22b3c761f1c36f41",
                    "source": {"arrow": "Right", "id": "node79c1a6173a292ce85d134781092a"},
                    "target": {"arrow": "Left", "id": "node1595e1f3508485c50f874c282c24"},
                },
                {
                    "id": "linee6e92c3334ef12f91e51877a3d86",
                    "source": {"arrow": "Right", "id": "node1a3fd48fa81f31db0cf2c13be697"},
                    "target": {"arrow": "Left", "id": "noded72838198dfc052149b5b1cd394b"},
                },
                {
                    "id": "line6057bece09e3e21a6c89b78f9104",
                    "source": {"arrow": "Right", "id": "noded72838198dfc052149b5b1cd394b"},
                    "target": {"arrow": "Bottom", "id": "node922b2d2223e529643a48f530ee62"},
                },
                {
                    "id": "line92bd5be9e3eaa50e38534d98b7d3",
                    "source": {"arrow": "Right", "id": "nodef70519ccb22cef0575f22eec55c0"},
                    "target": {"arrow": "Left", "id": "node922b2d2223e529643a48f530ee62"},
                },
            ],
            "location": [
                {"id": "node04f13d4060e03d5a9baee9aee139", "type": "startpoint", "x": 20, "y": 160},
                {
                    "id": "node79c1a6173a292ce85d134781092a",
                    "type": "tasknode",
                    "name": "消息展示",
                    "stage_name": "",
                    "x": 105,
                    "y": 150,
                },
                {"id": "node1595e1f3508485c50f874c282c24", "type": "branchgateway", "name": "", "x": 336, "y": 160},
                {
                    "id": "nodef70519ccb22cef0575f22eec55c0",
                    "type": "tasknode",
                    "name": "消息展示",
                    "stage_name": "",
                    "x": 557,
                    "y": 150,
                    "group": "蓝鲸服务(BK)",
                    "icon": "",
                },
                {
                    "id": "node1a3fd48fa81f31db0cf2c13be697",
                    "type": "tasknode",
                    "name": "消息展示",
                    "stage_name": "",
                    "x": 557,
                    "y": 258,
                    "group": "蓝鲸服务(BK)",
                    "icon": "",
                },
                {
                    "id": "noded72838198dfc052149b5b1cd394b",
                    "type": "tasknode",
                    "name": "消息展示",
                    "stage_name": "",
                    "x": 788,
                    "y": 258,
                    "group": "蓝鲸服务(BK)",
                    "icon": "",
                },
                {"id": "node922b2d2223e529643a48f530ee62", "type": "endpoint", "x": 1019, "y": 160},
            ],
            "outputs": [],
            "start_event": {
                "id": "node04f13d4060e03d5a9baee9aee139",
                "incoming": "",
                "name": "",
                "outgoing": "line213fe156e33362bf2c167b499e96",
                "type": "EmptyStartEvent",
                "labels": [],
            },
        }
        self.constants = {
            "${bk_display_message}": {
                "name": "展示内容",
                "key": "${bk_display_message}",
                "desc": "",
                "custom_type": "",
                "source_info": {"nodef70519ccb22cef0575f22eec55c0": ["bk_display_message"]},
                "source_tag": "bk_display.bk_display_message",
                "value": "${a}",
                "show_type": "show",
                "source_type": "component_inputs",
                "validation": "",
                "index": 0,
                "version": "1.0",
                "form_schema": {"type": "textarea", "attrs": {"name": "展示内容", "hookable": True}},
                "plugin_code": "",
            },
            "${a}": {
                "custom_type": "input",
                "desc": "",
                "form_schema": {"type": "input", "attrs": {"name": "输入框", "hookable": True, "validation": []}},
                "index": 1,
                "key": "${a}",
                "name": "a",
                "show_type": "show",
                "source_info": {},
                "source_tag": "input.input",
                "source_type": "custom",
                "validation": "^.+$",
                "is_condition_hide": "false",
                "pre_render_mako": False,
                "value": "a",
                "version": "legacy",
            },
            "${b}": {
                "custom_type": "input",
                "desc": "",
                "form_schema": {"type": "input", "attrs": {"name": "输入框", "hookable": True, "validation": []}},
                "index": 2,
                "key": "${b}",
                "name": "b",
                "show_type": "show",
                "source_info": {},
                "source_tag": "input.input",
                "source_type": "custom",
                "validation": "^.+$",
                "is_condition_hide": "false",
                "pre_render_mako": False,
                "value": "",
                "version": "legacy",
            },
            "${c}": {
                "custom_type": "input",
                "desc": "",
                "form_schema": {"type": "input", "attrs": {"name": "输入框", "hookable": False, "validation": []}},
                "index": 3,
                "key": "${c}",
                "name": "c",
                "show_type": "show",
                "source_info": {},
                "source_tag": "input.input",
                "source_type": "custom",
                "validation": "^.+$",
                "is_condition_hide": "false",
                "pre_render_mako": False,
                "value": "c",
                "version": "legacy",
            },
        }
        self.extra_data = ({"executor": "admin", "project_id": 1, "biz_cc_id": 2},)

    def test_get_task_referenced_constants_without_b_value(self):
        """ b 的值为空， 不命中任何分支 """
        result = get_task_referenced_constants(self.pipeline_tree, self.constants, self.extra_data)
        self.assertEqual(set(result["referenced_constants"]), {"${a}", "${b}"})

    def test_get_task_referenced_constants_with_b_equals_to_1(self):
        """ b 的值为 1， 命中引用了变量${bk_display_message}的分支 """
        self.constants["${b}"]["value"] = "1"
        result = get_task_referenced_constants(self.pipeline_tree, self.constants, self.extra_data)
        self.assertEqual(set(result["referenced_constants"]), {"${a}", "${b}", "${bk_display_message}"})

    def test_get_task_referenced_constants_with_b_equals_to_2(self):
        """ b 的值为 2， 命中引用了变量c的分支 """
        self.constants["${b}"]["value"] = "2"
        result = get_task_referenced_constants(self.pipeline_tree, self.constants, self.extra_data)
        self.assertEqual(set(result["referenced_constants"]), {"${a}", "${b}", "${c}"})
