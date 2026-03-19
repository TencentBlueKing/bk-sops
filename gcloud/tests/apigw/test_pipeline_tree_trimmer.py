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

from gcloud.utils.pipeline_tree_trimmer import trim_pipeline_tree


def _make_sample_tree():
    """构造一个包含所有典型字段的 pipeline_tree"""
    return {
        "id": "root_pipeline",
        "name": "测试流程",
        "start_event": {
            "id": "start_node",
            "type": "EmptyStartEvent",
            "name": "开始",
            "incoming": "",
            "outgoing": "flow1",
        },
        "end_event": {
            "id": "end_node",
            "type": "EmptyEndEvent",
            "name": "结束",
            "incoming": "flow2",
            "outgoing": "",
        },
        "activities": {
            "node1": {
                "id": "node1",
                "type": "ServiceActivity",
                "name": "执行脚本",
                "incoming": "flow1",
                "outgoing": "flow2",
                "optional": True,
                "loop": None,
                "labels": [],
                "stage_name": "步骤1",
                "retryable": True,
                "skippable": True,
                "error_ignorable": False,
                "auto_retry": {"enabled": False},
                "timeout_config": {"enabled": False},
                "component": {
                    "code": "job_fast_execute_script",
                    "version": "v1.0",
                    "data": {
                        "job_script_source": {"hook": False, "need_render": True, "value": "manual"},
                        "job_content": {"hook": False, "need_render": True, "value": "echo hello"},
                        "ip_list": {"hook": True, "need_render": True, "value": "${ip_list}"},
                        "button_refresh": {"hook": False, "value": ""},
                        "empty_field": {"hook": False, "value": ""},
                    },
                },
            },
        },
        "gateways": {
            "gw1": {
                "id": "gw1",
                "type": "ExclusiveGateway",
                "name": "判断",
                "incoming": "f1",
                "outgoing": ["f2", "f3"],
                "conditions": {"f2": {"evaluate": "${result} == True"}},
                "default_condition": {"flow_id": "f3"},
                "labels": [],
            },
        },
        "flows": {
            "flow1": {
                "id": "flow1",
                "source": "start_node",
                "target": "node1",
                "is_default": False,
                "line": {"x": 1, "y": 2},
            },
            "flow2": {
                "id": "flow2",
                "source": "node1",
                "target": "end_node",
                "is_default": True,
            },
        },
        "constants": {
            "${ip_list}": {
                "key": "${ip_list}",
                "name": "IP列表",
                "desc": "目标IP",
                "source_type": "custom",
                "custom_type": "textarea",
                "value": {"hook": True, "value": ""},
                "source_tag": "",
                "source_info": {},
                "index": 1,
                "version": "legacy",
                "show_type": "show",
                "form_schema": {},
                "validation": "",
            },
        },
        "line": {"l1": {"source": {"id": "n1"}, "target": {"id": "n2"}}},
        "location": [{"id": "n1", "x": 100, "y": 200}],
    }


class TrimPipelineTreeTest(TestCase):
    def test_preserves_top_level_structure(self):
        result = trim_pipeline_tree(_make_sample_tree())
        for key in ("activities", "flows", "gateways", "constants", "start_event", "end_event"):
            self.assertIn(key, result)
        self.assertIn("id", result)
        self.assertIn("name", result)

    def test_removes_line_and_location(self):
        result = trim_pipeline_tree(_make_sample_tree())
        self.assertNotIn("line", result)
        self.assertNotIn("location", result)

    def test_activity_whitelist(self):
        result = trim_pipeline_tree(_make_sample_tree())
        node = result["activities"]["node1"]
        self.assertEqual(node["id"], "node1")
        self.assertEqual(node["type"], "ServiceActivity")
        self.assertEqual(node["name"], "执行脚本")
        self.assertEqual(node["stage_name"], "步骤1")
        self.assertTrue(node["retryable"])
        self.assertNotIn("incoming", node)
        self.assertNotIn("outgoing", node)
        self.assertNotIn("optional", node)
        self.assertNotIn("loop", node)
        self.assertNotIn("labels", node)
        self.assertNotIn("timeout_config", node)

    def test_component_data_hook_unwrap(self):
        result = trim_pipeline_tree(_make_sample_tree())
        data = result["activities"]["node1"]["component"]["data"]
        self.assertEqual(data["job_script_source"], "manual")
        self.assertEqual(data["ip_list"], "${ip_list}")

    def test_component_data_removes_blacklist(self):
        result = trim_pipeline_tree(_make_sample_tree())
        data = result["activities"]["node1"]["component"]["data"]
        self.assertNotIn("button_refresh", data)

    def test_component_data_removes_empty(self):
        result = trim_pipeline_tree(_make_sample_tree())
        data = result["activities"]["node1"]["component"]["data"]
        self.assertNotIn("empty_field", data)

    def test_gateway_whitelist(self):
        result = trim_pipeline_tree(_make_sample_tree())
        gw = result["gateways"]["gw1"]
        self.assertEqual(gw["id"], "gw1")
        self.assertEqual(gw["type"], "ExclusiveGateway")
        self.assertIn("conditions", gw)
        self.assertIn("default_condition", gw)
        self.assertNotIn("incoming", gw)
        self.assertNotIn("outgoing", gw)
        self.assertNotIn("labels", gw)

    def test_flow_preserves_source_target(self):
        result = trim_pipeline_tree(_make_sample_tree())
        f1 = result["flows"]["flow1"]
        self.assertEqual(f1["source"], "start_node")
        self.assertEqual(f1["target"], "node1")
        self.assertNotIn("line", f1)
        self.assertNotIn("id", f1)

    def test_flow_preserves_is_default(self):
        result = trim_pipeline_tree(_make_sample_tree())
        f2 = result["flows"]["flow2"]
        self.assertTrue(f2["is_default"])

    def test_event_keeps_only_id_type_name(self):
        result = trim_pipeline_tree(_make_sample_tree())
        start = result["start_event"]
        self.assertEqual(set(start.keys()), {"id", "type", "name"})

    def test_constants_whitelist(self):
        result = trim_pipeline_tree(_make_sample_tree())
        const = result["constants"]["${ip_list}"]
        self.assertEqual(const["key"], "${ip_list}")
        self.assertEqual(const["name"], "IP列表")
        self.assertNotIn("index", const)
        self.assertNotIn("version", const)
        self.assertNotIn("show_type", const)
        self.assertNotIn("form_schema", const)

    def test_constants_value_hook_unwrap(self):
        result = trim_pipeline_tree(_make_sample_tree())
        const = result["constants"]["${ip_list}"]
        self.assertNotIn("value", const)  # unwrapped value is "" which is empty, so removed

    def test_subprocess_recursion(self):
        tree = {
            "id": "root",
            "activities": {
                "sub1": {
                    "id": "sub1",
                    "type": "SubProcess",
                    "name": "子流程",
                    "template_id": 100,
                    "template_source": "project",
                    "version": "v1",
                    "pipeline": {
                        "id": "sub_pipeline",
                        "activities": {},
                        "gateways": {},
                        "flows": {},
                        "constants": {},
                        "start_event": {"id": "s1", "type": "EmptyStartEvent", "name": ""},
                        "end_event": {"id": "e1", "type": "EmptyEndEvent", "name": ""},
                        "line": {"should": "be removed"},
                        "location": [{"should": "be removed"}],
                    },
                },
            },
            "gateways": {},
            "flows": {},
            "constants": {},
            "start_event": {"id": "s0", "type": "EmptyStartEvent", "name": ""},
            "end_event": {"id": "e0", "type": "EmptyEndEvent", "name": ""},
        }
        result = trim_pipeline_tree(tree)
        sub = result["activities"]["sub1"]
        self.assertEqual(sub["template_id"], 100)
        self.assertNotIn("line", sub["pipeline"])
        self.assertNotIn("location", sub["pipeline"])

    def test_preserves_converge_gateway_id(self):
        tree = {
            "id": "root",
            "activities": {},
            "gateways": {
                "pg1": {
                    "id": "pg1",
                    "type": "ParallelGateway",
                    "name": "",
                    "converge_gateway_id": "cg1",
                    "incoming": "f1",
                    "outgoing": ["f2", "f3"],
                },
            },
            "flows": {},
            "constants": {},
            "start_event": {"id": "s", "type": "EmptyStartEvent", "name": ""},
            "end_event": {"id": "e", "type": "EmptyEndEvent", "name": ""},
        }
        result = trim_pipeline_tree(tree)
        self.assertEqual(result["gateways"]["pg1"]["converge_gateway_id"], "cg1")

    def test_non_dict_input_returns_as_is(self):
        self.assertIsNone(trim_pipeline_tree(None))
        self.assertEqual(trim_pipeline_tree("string"), "string")
        self.assertEqual(trim_pipeline_tree([1, 2]), [1, 2])
