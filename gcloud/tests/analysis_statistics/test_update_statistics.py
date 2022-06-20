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

from gcloud.analysis_statistics import variable
from gcloud.analysis_statistics.models import TemplateVariableStatistics


class VairableModuleTestCase(TestCase):
    def test_update_statistics(self):
        self.maxDiff = None
        project_id = 1
        template_id = 2
        pipeline_tree = {
            "activities": {
                "node2c847688221378a9e17ca7380a86": {
                    "component": {
                        "code": "sleep_timer",
                        "data": {
                            "bk_timing": {"hook": True, "need_render": True, "value": "${bk_timing}"},
                            "force_check": {"hook": False, "need_render": True, "value": True},
                        },
                        "version": "legacy",
                    },
                    "id": "node2c847688221378a9e17ca7380a86",
                    "type": "ServiceActivity",
                },
                "node9e4fec70dcd1460d1314f49f1917": {
                    "component": {
                        "code": "sleep_timer",
                        "data": {
                            "bk_timing": {"hook": False, "need_render": True, "value": "${time}${_system.task_id}"},
                            "force_check": {"hook": False, "need_render": True, "value": True},
                        },
                        "version": "legacy",
                    },
                    "id": "node9e4fec70dcd1460d1314f49f1917",
                    "type": "ServiceActivity",
                },
                "node3e5b73f43b3e3c97773f6fd6b6f6": {
                    "component": {
                        "code": "sleep_timer",
                        "data": {
                            "bk_timing": {"hook": False, "need_render": True, "value": "${_env_key1}${time}"},
                            "force_check": {"hook": False, "need_render": True, "value": True},
                        },
                        "version": "legacy",
                    },
                    "id": "node3e5b73f43b3e3c97773f6fd6b6f6",
                    "type": "ServiceActivity",
                },
            },
            "gateways": {},
            "constants": {
                "${bk_timing}": {
                    "name": "定时时间",
                    "key": "${bk_timing}",
                    "desc": "",
                    "custom_type": "",
                    "source_info": {"node2c847688221378a9e17ca7380a86": ["bk_timing"]},
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
                "${time}": {
                    "custom_type": "input",
                    "desc": "",
                    "form_schema": {"type": "input", "attrs": {"name": "输入框", "hookable": True, "validation": []}},
                    "index": 1,
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
                    "index": 2,
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
                "${select}": {
                    "custom_type": "select",
                    "desc": "",
                    "form_schema": {},
                    "index": 3,
                    "key": "${select}",
                    "name": "select",
                    "show_type": "show",
                    "source_info": {},
                    "source_tag": "select.select",
                    "source_type": "custom",
                    "validation": "",
                    "is_condition_hide": False,
                    "pre_render_mako": False,
                    "value": {"datasource": "0", "items_text": "1", "type": "0", "default": "1"},
                    "version": "legacy",
                    "is_meta": True,
                },
            },
        }
        custom_constants_types = variable.update_statistics(
            project_id=project_id, template_id=template_id, pipeline_tree=pipeline_tree
        )

        self.assertEqual(custom_constants_types, {"input.input", "var_cmdb_ip_selector.ip_selector", "select.select"})

        statistics = TemplateVariableStatistics.objects.all().values()
        self.assertEqual(len(statistics), 5)

        statistic_dict = {}
        for s in statistics:
            s.pop("id")
            statistic_dict[s["variable_key"]] = s
        self.assertEqual(
            statistic_dict,
            {
                "${_env_key1}": {
                    "template_id": 2,
                    "project_id": 1,
                    "variable_key": "${_env_key1}",
                    "variable_type": "",
                    "variable_source": "project",
                    "refs": 1,
                },
                "${bk_timing}": {
                    "template_id": 2,
                    "project_id": 1,
                    "variable_key": "${bk_timing}",
                    "variable_type": "sleep_timer.bk_timing",
                    "variable_source": "component_inputs",
                    "refs": 1,
                },
                "${ip}": {
                    "template_id": 2,
                    "project_id": 1,
                    "variable_key": "${ip}",
                    "variable_type": "var_cmdb_ip_selector.ip_selector",
                    "variable_source": "custom",
                    "refs": 0,
                },
                "${select}": {
                    "template_id": 2,
                    "project_id": 1,
                    "variable_key": "${select}",
                    "variable_type": "select.select",
                    "variable_source": "custom",
                    "refs": 0,
                },
                "${time}": {
                    "template_id": 2,
                    "project_id": 1,
                    "variable_key": "${time}",
                    "variable_type": "input.input",
                    "variable_source": "custom",
                    "refs": 2,
                },
            },
        )
