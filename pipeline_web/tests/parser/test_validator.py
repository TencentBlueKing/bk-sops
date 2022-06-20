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

import unittest

from pipeline_web import exceptions
from pipeline_web.parser import validator


class TestValidator(unittest.TestCase):
    def setUp(self) -> None:
        self.valid_tree = {
            "name": "new20220314102949",
            "activities": {
                "node5cf2e6f4b96746f5ef3795d2152f": {
                    "component": {
                        "code": "sleep_timer",
                        "data": {
                            "bk_timing": {"hook": True, "need_render": True, "value": "${bk_timing}"},
                            "force_check": {"hook": False, "need_render": True, "value": True},
                        },
                        "version": "legacy",
                    },
                    "error_ignorable": False,
                    "id": "node5cf2e6f4b96746f5ef3795d2152f",
                    "incoming": ["line8ca9763e0f5e9499c4fc1160dbfc"],
                    "loop": None,
                    "name": "定时",
                    "optional": True,
                    "outgoing": "line2f5641e893efb4863cb92314b527",
                    "stage_name": "",
                    "type": "ServiceActivity",
                    "retryable": True,
                    "skippable": True,
                    "auto_retry": {"enable": False, "interval": 0, "times": 1},
                    "timeout_config": {"enable": False, "seconds": 10, "action": "forced_fail"},
                    "labels": [],
                },
                "node0b4e9c17b70fe9f47369e8a19861": {
                    "component": {
                        "code": "sleep_timer",
                        "data": {
                            "bk_timing": {"hook": False, "need_render": True, "value": "${time|"},
                            "force_check": {"hook": False, "need_render": True, "value": True},
                        },
                        "version": "legacy",
                    },
                    "error_ignorable": False,
                    "id": "node0b4e9c17b70fe9f47369e8a19861",
                    "incoming": ["line2f5641e893efb4863cb92314b527"],
                    "loop": None,
                    "name": "定时",
                    "optional": True,
                    "outgoing": "linee9a495282a6c2cfb70b0f0af9e2b",
                    "stage_name": "",
                    "type": "ServiceActivity",
                    "retryable": True,
                    "skippable": True,
                    "auto_retry": {"enable": False, "interval": 0, "times": 1},
                    "timeout_config": {"enable": False, "seconds": 10, "action": "forced_fail"},
                    "labels": [],
                },
            },
            "end_event": {
                "id": "node1eacb50f98d20d96bc2ddd8ceb14",
                "incoming": ["linee9a495282a6c2cfb70b0f0af9e2b"],
                "name": "",
                "outgoing": "",
                "type": "EmptyEndEvent",
            },
            "flows": {
                "line8ca9763e0f5e9499c4fc1160dbfc": {
                    "id": "line8ca9763e0f5e9499c4fc1160dbfc",
                    "is_default": False,
                    "source": "node1108c3c2493688d8eff1b9290db0",
                    "target": "node5cf2e6f4b96746f5ef3795d2152f",
                },
                "line2f5641e893efb4863cb92314b527": {
                    "id": "line2f5641e893efb4863cb92314b527",
                    "is_default": False,
                    "source": "node5cf2e6f4b96746f5ef3795d2152f",
                    "target": "node0b4e9c17b70fe9f47369e8a19861",
                },
                "linee9a495282a6c2cfb70b0f0af9e2b": {
                    "id": "linee9a495282a6c2cfb70b0f0af9e2b",
                    "is_default": False,
                    "source": "node0b4e9c17b70fe9f47369e8a19861",
                    "target": "node1eacb50f98d20d96bc2ddd8ceb14",
                },
            },
            "gateways": {},
            "line": [
                {
                    "id": "line8ca9763e0f5e9499c4fc1160dbfc",
                    "source": {"arrow": "Right", "id": "node1108c3c2493688d8eff1b9290db0"},
                    "target": {"arrow": "Left", "id": "node5cf2e6f4b96746f5ef3795d2152f"},
                },
                {
                    "source": {"arrow": "Right", "id": "node5cf2e6f4b96746f5ef3795d2152f"},
                    "target": {"id": "node0b4e9c17b70fe9f47369e8a19861", "arrow": "Left"},
                    "id": "line2f5641e893efb4863cb92314b527",
                },
                {
                    "source": {"arrow": "Right", "id": "node0b4e9c17b70fe9f47369e8a19861"},
                    "target": {"id": "node1eacb50f98d20d96bc2ddd8ceb14", "arrow": "Left"},
                    "id": "linee9a495282a6c2cfb70b0f0af9e2b",
                },
            ],
            "location": [
                {"id": "node1108c3c2493688d8eff1b9290db0", "x": 40, "y": 150, "type": "startpoint"},
                {
                    "id": "node5cf2e6f4b96746f5ef3795d2152f",
                    "x": 140,
                    "y": 140,
                    "name": "定时",
                    "stage_name": "",
                    "type": "tasknode",
                    "mode": "edit",
                    "icon": "",
                    "group": "蓝鲸服务(BK)",
                    "code": "sleep_timer",
                    "status": "",
                    "skippable": True,
                    "retryable": True,
                    "optional": True,
                    "auto_retry": {"enable": False, "interval": 0, "times": 1},
                    "timeout_config": {"enable": False, "seconds": 10, "action": "forced_fail"},
                    "phase": 0,
                },
                {"id": "node1eacb50f98d20d96bc2ddd8ceb14", "x": 600, "y": 150, "type": "endpoint"},
                {
                    "id": "node0b4e9c17b70fe9f47369e8a19861",
                    "x": 340,
                    "y": 140,
                    "name": "定时",
                    "stage_name": "",
                    "type": "tasknode",
                    "mode": "edit",
                    "icon": "",
                    "group": "蓝鲸服务(BK)",
                    "code": "sleep_timer",
                    "status": "",
                    "skippable": True,
                    "retryable": True,
                    "optional": True,
                    "auto_retry": {"enable": False, "interval": 0, "times": 1},
                    "timeout_config": {"enable": False, "seconds": 10, "action": "forced_fail"},
                    "phase": 0,
                    "oldSouceId": "node5cf2e6f4b96746f5ef3795d2152f",
                    "isActived": False,
                },
            ],
            "outputs": [],
            "start_event": {
                "id": "node1108c3c2493688d8eff1b9290db0",
                "incoming": "",
                "name": "",
                "outgoing": "line8ca9763e0f5e9499c4fc1160dbfc",
                "type": "EmptyStartEvent",
            },
            "template_id": "",
            "constants": {
                "${bk_timing}": {
                    "name": "定时时间",
                    "key": "${bk_timing}",
                    "desc": "",
                    "custom_type": "",
                    "source_info": {"node5cf2e6f4b96746f5ef3795d2152f": ["bk_timing"]},
                    "source_tag": "sleep_timer.bk_timing",
                    "value": "",
                    "show_type": "show",
                    "source_type": "component_inputs",
                    "validation": "",
                    "index": 0,
                    "version": "legacy",
                    "form_schema": {
                        "type": "input",
                        "attrs": {
                            "name": "定时时间",
                            "placeholder": "秒(s) 或 时间(%Y-%m-%d %H:%M:%S)",
                            "hookable": True,
                            "validation": [{"type": "required"}],
                        },
                    },
                    "plugin_code": "",
                },
                "${_result}": {
                    "name": "执行结果",
                    "key": "${_result}",
                    "desc": "",
                    "custom_type": "",
                    "source_info": {"node5cf2e6f4b96746f5ef3795d2152f": ["_result"]},
                    "source_tag": "",
                    "value": "",
                    "show_type": "hide",
                    "source_type": "component_outputs",
                    "validation": "",
                    "index": 1,
                    "version": "legacy",
                    "plugin_code": "",
                },
                "${time}": {
                    "custom_type": "input",
                    "desc": "",
                    "form_schema": {"type": "input", "attrs": {"name": "输入框", "hookable": True, "validation": []}},
                    "index": 3,
                    "key": "${time}",
                    "name": "time",
                    "show_type": "show",
                    "source_info": {},
                    "source_tag": "input.input",
                    "source_type": "custom",
                    "validation": "^.+$",
                    "is_condition_hide": False,
                    "pre_render_mako": False,
                    "value": "",
                    "version": "legacy",
                },
                "${ip}": {
                    "custom_type": "ip_selector",
                    "desc": "",
                    "form_schema": {
                        "type": "ip_selector",
                        "attrs": {
                            "name": "选择服务器",
                            "hookable": True,
                            "isMultiple": False,
                            "validation": [{"type": "required"}],
                            "default": {
                                "selectors": ["ip"],
                                "topo": [],
                                "ip": [],
                                "filters": [],
                                "excludes": [],
                                "with_cloud_id": False,
                                "separator": ",",
                            },
                        },
                    },
                    "index": 4,
                    "key": "${ip}",
                    "name": "ip",
                    "show_type": "show",
                    "source_info": {},
                    "source_tag": "var_cmdb_ip_selector.ip_selector",
                    "source_type": "custom",
                    "validation": "",
                    "is_condition_hide": False,
                    "pre_render_mako": False,
                    "value": {
                        "selectors": ["ip"],
                        "topo": [],
                        "ip": [],
                        "filters": [],
                        "excludes": [],
                        "with_cloud_id": False,
                        "separator": ",",
                    },
                    "version": "legacy",
                    "is_meta": False,
                },
            },
        }

    def test_valid_pipeline_tree(self):
        validator.validate_web_pipeline_tree(self.valid_tree)

    def test_invalid_constants_key__value_not_match(self):
        invalid_tree = self.valid_tree
        invalid_tree["constants"]["${invalid_key}"] = {
            "custom_type": "input",
            "desc": "",
            "form_schema": {"type": "input", "attrs": {"name": "输入框", "hookable": True, "validation": []}},
            "index": 3,
            "key": "${time}",
            "name": "time",
            "show_type": "show",
            "source_info": {},
            "source_tag": "input.input",
            "source_type": "custom",
            "validation": "^.+$",
            "is_condition_hide": False,
            "pre_render_mako": False,
            "value": "",
            "version": "legacy",
        }
        self.assertRaises(exceptions.ParserWebTreeException, validator.validate_web_pipeline_tree, invalid_tree)

    def test_invalid_constants_key__pattern_start_with__env(self):
        invalid_tree = self.valid_tree
        invalid_tree["constants"]["${_env_key}"] = {
            "custom_type": "input",
            "desc": "",
            "form_schema": {"type": "input", "attrs": {"name": "输入框", "hookable": True, "validation": []}},
            "index": 3,
            "key": "${_env_key}",
            "name": "time",
            "show_type": "show",
            "source_info": {},
            "source_tag": "input.input",
            "source_type": "custom",
            "validation": "^.+$",
            "is_condition_hide": False,
            "pre_render_mako": False,
            "value": "",
            "version": "legacy",
        }
        self.assertRaises(exceptions.ParserWebTreeException, validator.validate_web_pipeline_tree, invalid_tree)

    def test_invalid_outputs_key__pattern_start_with__env(self):
        invalid_tree = self.valid_tree
        invalid_tree["outputs"].append("${_env_key}")
        self.assertRaises(exceptions.ParserWebTreeException, validator.validate_web_pipeline_tree, invalid_tree)

    def test_invalid_constants_key__pattern_not_start_with_dollar(self):
        invalid_tree = self.valid_tree
        invalid_tree["constants"]["key"] = {
            "custom_type": "input",
            "desc": "",
            "form_schema": {"type": "input", "attrs": {"name": "输入框", "hookable": True, "validation": []}},
            "index": 3,
            "key": "key",
            "name": "time",
            "show_type": "show",
            "source_info": {},
            "source_tag": "input.input",
            "source_type": "custom",
            "validation": "^.+$",
            "is_condition_hide": False,
            "pre_render_mako": False,
            "value": "",
            "version": "legacy",
        }
        self.assertRaises(exceptions.ParserWebTreeException, validator.validate_web_pipeline_tree, invalid_tree)

    def test_invalid_outputs_key__pattern_not_start_with_dollar(self):
        invalid_tree = self.valid_tree
        invalid_tree["outputs"].append("key")
        self.assertRaises(exceptions.ParserWebTreeException, validator.validate_web_pipeline_tree, invalid_tree)

    def test_invalid_constants_key__pattern_start_with_system(self):
        invalid_tree = self.valid_tree
        invalid_tree["constants"]["${system.key}"] = {
            "custom_type": "input",
            "desc": "",
            "form_schema": {"type": "input", "attrs": {"name": "输入框", "hookable": True, "validation": []}},
            "index": 3,
            "key": "${system.key}",
            "name": "time",
            "show_type": "show",
            "source_info": {},
            "source_tag": "input.input",
            "source_type": "custom",
            "validation": "^.+$",
            "is_condition_hide": False,
            "pre_render_mako": False,
            "value": "",
            "version": "legacy",
        }
        self.assertRaises(exceptions.ParserWebTreeException, validator.validate_web_pipeline_tree, invalid_tree)

    def test_invalid_outputs_key__pattern_start_with_system(self):
        invalid_tree = self.valid_tree
        invalid_tree["outputs"].append("${system.key}")
        self.assertRaises(exceptions.ParserWebTreeException, validator.validate_web_pipeline_tree, invalid_tree)
