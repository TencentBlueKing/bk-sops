# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from django.test import TestCase

from pipeline_web.parser.format import classify_constants


class ClassifyConstantsTestCase(TestCase):
    def test_normal(self):
        """
        正常情况的一种测试用例
        """
        constants = {
            "${bk_timing}": {
                "name": "定时时间",
                "key": "${bk_timing}",
                "desc": "",
                "custom_type": "",
                "source_info": {"node38f09be9ba7402ec05186c562c0e": ["bk_timing"]},
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
                        "validation": [{"type": "required"}, {"type": "custom"}],
                    },
                },
            },
            "${_result}": {
                "name": "执行结果",
                "key": "${_result}",
                "desc": "",
                "custom_type": "",
                "source_info": {"node38f09be9ba7402ec05186c562c0e": ["_result"]},
                "source_tag": "",
                "value": "",
                "show_type": "hide",
                "source_type": "component_outputs",
                "validation": "",
                "index": 1,
                "version": "legacy",
            },
            "${custom}": {
                "custom_type": "input",
                "desc": "",
                "form_schema": {"type": "input", "attrs": {"name": "输入框", "hookable": True, "validation": []}},
                "index": 3,
                "key": "${custom}",
                "name": "custom",
                "show_type": "show",
                "source_info": {},
                "source_tag": "input.input",
                "source_type": "custom",
                "validation": "^.+$",
                "value": "${bk_timing}",
                "version": "legacy",
            },
        }
        expect_outputs = {
            "constant_pool": {
                "${bk_timing}": {
                    "name": "定时时间",
                    "key": "${bk_timing}",
                    "desc": "",
                    "custom_type": "",
                    "source_info": {"node38f09be9ba7402ec05186c562c0e": ["bk_timing"]},
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
                            "validation": [{"type": "required"}, {"type": "custom"}],
                        },
                    },
                    "is_param": True,
                },
                "${custom}": {
                    "custom_type": "input",
                    "desc": "",
                    "form_schema": {"type": "input", "attrs": {"name": "输入框", "hookable": True, "validation": []}},
                    "index": 3,
                    "key": "${custom}",
                    "name": "custom",
                    "show_type": "show",
                    "source_info": {},
                    "source_tag": "input.input",
                    "source_type": "custom",
                    "validation": "^.+$",
                    "value": "${bk_timing}",
                    "version": "legacy",
                    "is_param": True,
                },
            },
            "data_inputs": {
                "${_result}": {
                    "type": "splice",
                    "source_act": "node38f09be9ba7402ec05186c562c0e",
                    "source_key": "_result",
                    "value": "",
                    "is_param": False,
                }
            },
            "acts_outputs": {"node38f09be9ba7402ec05186c562c0e": {"_result": "${_result}"}},
            "params": {},
        }
        self.assertEqual(classify_constants(constants, False), expect_outputs)

    def test_outputs_node_cancel(self):
        """
        测试带有输出变量的节点被取消勾选的情况
        """
        constants = {
            "${bk_timing}": {
                "name": "定时时间",
                "key": "${bk_timing}",
                "desc": "",
                "custom_type": "",
                "source_info": {"node38f09be9ba7402ec05186c562c0e": ["bk_timing"]},
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
                        "validation": [{"type": "required"}, {"type": "custom"}],
                    },
                },
            },
            "${_result}": {
                "name": "执行结果",
                "key": "${_result}",
                "desc": "",
                "custom_type": "",
                "source_info": {},
                "source_tag": "",
                "value": "",
                "show_type": "hide",
                "source_type": "component_outputs",
                "validation": "",
                "index": 1,
                "version": "legacy",
            },
            "${custom}": {
                "custom_type": "input",
                "desc": "",
                "form_schema": {"type": "input", "attrs": {"name": "输入框", "hookable": True, "validation": []}},
                "index": 3,
                "key": "${custom}",
                "name": "custom",
                "show_type": "show",
                "source_info": {},
                "source_tag": "input.input",
                "source_type": "custom",
                "validation": "^.+$",
                "value": "${bk_timing}",
                "version": "legacy",
            },
        }
        expect_outputs = {
            "constant_pool": {
                "${bk_timing}": {
                    "name": "定时时间",
                    "key": "${bk_timing}",
                    "desc": "",
                    "custom_type": "",
                    "source_info": {"node38f09be9ba7402ec05186c562c0e": ["bk_timing"]},
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
                            "validation": [{"type": "required"}, {"type": "custom"}],
                        },
                    },
                    "is_param": True,
                },
                "${custom}": {
                    "custom_type": "input",
                    "desc": "",
                    "form_schema": {"type": "input", "attrs": {"name": "输入框", "hookable": True, "validation": []}},
                    "index": 3,
                    "key": "${custom}",
                    "name": "custom",
                    "show_type": "show",
                    "source_info": {},
                    "source_tag": "input.input",
                    "source_type": "custom",
                    "validation": "^.+$",
                    "value": "${bk_timing}",
                    "version": "legacy",
                    "is_param": True,
                },
            },
            "data_inputs": {},
            "acts_outputs": {},
            "params": {},
        }
        self.assertEqual(classify_constants(constants, False), expect_outputs)
