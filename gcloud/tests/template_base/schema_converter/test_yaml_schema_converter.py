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
import json
import os

import yaml
from django.test import TestCase

from gcloud.template_base.domains.converter_handler import YamlSchemaConverterHandler


class YamlSchemaConverterTestCase(TestCase):
    def setUp(self):
        self.dir_path = os.path.dirname(os.path.abspath(__file__))
        with open("{}/test_complicated_data.json".format(self.dir_path), encoding="utf-8") as infile:
            self.original_data = json.load(infile)
        with open("{}/test_complicated_yaml_data.yaml".format(self.dir_path), encoding="utf-8") as infile:
            self.yaml_docs = list(yaml.safe_load_all(infile))

        self.convert_handler = YamlSchemaConverterHandler(version="v1")

    @staticmethod
    def _check_reconvert_correct(reconverted_data, original_data):
        original_trees = {
            template["name"]: template["tree"]
            for _, template in original_data["pipeline_template_data"]["template"].items()
        }
        reconverted_trees = {template["name"]: template["tree"] for _, template in reconverted_data.items()}
        if len(original_trees) != len(reconverted_trees):
            return False
        # TODO: 暂时校验逻辑较弱，后续需加强
        for name, original_tree in original_trees.items():
            reconverted_tree = reconverted_trees[name]
            for key in ["activities", "constants", "flows", "line", "gateways", "outputs", "location"]:
                if len(reconverted_tree[key]) != len(original_tree[key]):
                    return False
        return True

    def test_convert_yaml(self):
        self.maxDiff = None
        convert_result = self.convert_handler.convert(self.original_data)
        yaml_data = convert_result["data"]
        self.assertEqual(yaml_data, self.yaml_docs)

    def test_reconvert_yaml(self):
        reconvert_result = self.convert_handler.reconvert(self.yaml_docs)
        generated_data = reconvert_result["data"]["templates"]
        self.assertTrue(self._check_reconvert_correct(generated_data, self.original_data))

    def test_reconvert_with_external_subprocess_template_id_as_int(self):
        class _FakeTemplateObj:
            def __init__(self, pk, project_id, pipeline_tree):
                self.pk = pk
                self.project_id = project_id
                self.pipeline_tree = pipeline_tree

        class _FakeQuerySet(list):
            def filter(self, **kwargs):
                data = list(self)
                if "project_id" in kwargs:
                    data = [obj for obj in data if obj.project_id == kwargs["project_id"]]
                if "pk__in" in kwargs:
                    target_ids = {str(pk) for pk in kwargs["pk__in"]}
                    data = [obj for obj in data if str(obj.pk) in target_ids]
                return _FakeQuerySet(data)

        class _FakeTemplateModel:
            objects = _FakeQuerySet(
                [
                    _FakeTemplateObj(
                        1001,
                        10,
                        {
                            "constants": {
                                "sub_const": {"name": "sub_const", "source_type": "custom", "value": "value"},
                            }
                        },
                    )
                ]
            )

        yaml_docs = [
            {
                "schema_version": "v1",
                "meta": {"name": "parent", "id": "parent_template"},
                "spec": {
                    "nodes": [
                        {"type": "EmptyStartEvent", "id": "start", "next": ["sub"]},
                        {
                            "type": "SubProcess",
                            "id": "sub",
                            "name": "sub",
                            "template_id": 1001,
                            "always_use_latest": False,
                            "next": ["end"],
                        },
                        {"type": "EmptyEndEvent", "id": "end"},
                    ]
                },
            }
        ]

        reconvert_result = self.convert_handler.reconvert(
            yaml_docs, template_model_cls=_FakeTemplateModel, project_id=10
        )
        self.assertTrue(reconvert_result["result"])
        templates = reconvert_result["data"]["templates"]
        self.assertIn("parent_template", templates)
        subprocess_node = next(
            activity
            for activity in templates["parent_template"]["tree"]["activities"].values()
            if activity["type"] == "SubProcess"
        )
        self.assertIn("sub_const", subprocess_node["constants"])

    def test_converter_remove_loop_by_bfs(self):
        nodes = {
            1: {"last": [], "next": [2]},
            2: {"last": [1, 4], "next": [3]},
            3: {"last": [2], "next": [4]},
            4: {"last": [3], "next": [5, 2]},
            5: {"last": [4], "next": []},
        }
        result_nodes = {
            1: {"last": [], "next": [2]},
            2: {"last": [1], "next": [3]},
            3: {"last": [2], "next": [4]},
            4: {"last": [3], "next": [5]},
            5: {"last": [4], "next": []},
        }
        start_node_id = 1
        self.convert_handler.converter._remove_loop_by_bfs(nodes, start_node_id)
        self.assertEqual(nodes, result_nodes)

    def test_converter_calculate_nodes_orders(self):
        nodes = {
            1: {"last": [], "next": [2, 4]},
            2: {"last": [1], "next": [3]},
            3: {"last": [2], "next": [6]},
            4: {"last": [1], "next": [5]},
            5: {"last": [4], "next": [6]},
            6: {"last": [3, 5], "next": []},
        }
        start_node_id = 1
        ordered_node_ids = self.convert_handler.converter._calculate_nodes_orders(nodes, start_node_id)
        self.assertIn(ordered_node_ids, [[1, 2, 3, 4, 5, 6], [1, 4, 5, 2, 3, 6]])

    def test_converter_convert_constants(self):
        with open("{}/test_yaml_data.yaml".format(self.dir_path), encoding="utf-8") as infile:
            yaml_docs = list(yaml.safe_load_all(infile))
        with open("{}/test_original_data.json".format(self.dir_path), encoding="utf-8") as infile:
            original_data = json.load(infile)
        yaml_constants = yaml_docs[0]["spec"]["constants"]
        yaml_param_constants = {
            "component_inputs": {},
            "component_outputs": {
                "node413dba1a74e3045da403e3be9cd5": {"_loop": {"name": "循环次数", "key": "${_loop}", "hide": True}}
            },
        }
        template_id = "n2125aebb4c8334f8ba4d575315a8d94"
        constants = original_data["pipeline_template_data"]["template"][template_id]["tree"]["constants"]
        converted_constants, param_constants = self.convert_handler.converter._convert_constants(constants)
        self.assertEqual(converted_constants, yaml_constants)
        self.assertEqual(param_constants, yaml_param_constants)

    @staticmethod
    def _build_yaml_docs(activity_extra: dict):
        """构造仅含一个 ServiceActivity 的最小可用 YAML 文档"""
        node = {
            "id": "act1",
            "type": "ServiceActivity",
            "name": "测试节点",
            "component": {"code": "bk_display", "data": {}, "version": "1.0"},
            "auto_retry": {"enable": False, "interval": 0, "times": 1},
            "stage_name": "默认",
            "ignore_error": False,
            "can_retry": True,
            "can_skip": True,
            "next": ["end"],
        }
        node.update(activity_extra)
        return [
            {
                "schema_version": "v1",
                "meta": {"name": "测试模版", "id": "test_template"},
                "spec": {
                    "nodes": [
                        {"id": "start", "type": "EmptyStartEvent", "next": ["act1"]},
                        node,
                        {"id": "end", "type": "EmptyEndEvent"},
                    ]
                },
            }
        ]

    def test_validate_service_activity_config_all_closed(self):
        """所有容错字段关闭（默认值）应通过校验"""
        yaml_docs = self._build_yaml_docs({})
        result = self.convert_handler.converter.validate_data(yaml_docs)
        self.assertTrue(result["result"], msg=result.get("message"))

    def test_validate_service_activity_config_legacy_yaml_without_fields(self):
        """兼容历史 YAML：ServiceActivity 完全不带容错/控制类字段应通过校验"""
        # 历史导出的 YAML 可能只有基础字段，不含 ignore_error/can_retry/can_skip/auto_retry/timeout_config
        legacy_node = {
            "id": "act1",
            "type": "ServiceActivity",
            "name": "测试节点",
            "component": {"code": "bk_display", "data": {}, "version": "1.0"},
            "stage_name": "默认",
            "next": ["end"],
        }
        yaml_docs = [
            {
                "schema_version": "v1",
                "meta": {"name": "测试模版", "id": "test_template"},
                "spec": {
                    "nodes": [
                        {"id": "start", "type": "EmptyStartEvent", "next": ["act1"]},
                        legacy_node,
                        {"id": "end", "type": "EmptyEndEvent"},
                    ]
                },
            }
        ]
        result = self.convert_handler.converter.validate_data(yaml_docs)
        self.assertTrue(result["result"], msg=result.get("message"))

    def test_validate_service_activity_config_single_enabled(self):
        """仅开启一个策略开关应通过校验"""
        # 开启自动跳过后，按规则必须关闭可重试(can_retry)，否则视为冲突配置
        yaml_docs = self._build_yaml_docs({"ignore_error": True, "can_retry": False})
        result = self.convert_handler.converter.validate_data(yaml_docs)
        self.assertTrue(result["result"], msg=result.get("message"))

        yaml_docs = self._build_yaml_docs({"auto_retry": {"enable": True, "interval": 0, "times": 1}})
        result = self.convert_handler.converter.validate_data(yaml_docs)
        self.assertTrue(result["result"], msg=result.get("message"))

        yaml_docs = self._build_yaml_docs({"timeout_config": {"enable": True, "seconds": 10, "action": "forced_fail"}})
        result = self.convert_handler.converter.validate_data(yaml_docs)
        self.assertTrue(result["result"], msg=result.get("message"))

    def test_validate_service_activity_config_ignore_error_and_auto_retry(self):
        """自动跳过 + 自动重试 同时开启应校验失败"""
        yaml_docs = self._build_yaml_docs(
            {"ignore_error": True, "auto_retry": {"enable": True, "interval": 0, "times": 1}}
        )
        result = self.convert_handler.converter.validate_data(yaml_docs)
        self.assertFalse(result["result"])
        self.assertIn("不能同时开启两个或两个以上", str(result["message"]))

    def test_validate_service_activity_config_ignore_error_and_timeout(self):
        """自动跳过 + 超时控制 同时开启应校验失败"""
        yaml_docs = self._build_yaml_docs(
            {"ignore_error": True, "timeout_config": {"enable": True, "seconds": 10, "action": "forced_fail"}}
        )
        result = self.convert_handler.converter.validate_data(yaml_docs)
        self.assertFalse(result["result"])
        self.assertIn("不能同时开启两个或两个以上", str(result["message"]))

    def test_validate_service_activity_config_ignore_error_with_retry(self):
        """开启自动跳过后配置可重试(can_retry=True)应校验失败"""
        yaml_docs = self._build_yaml_docs({"ignore_error": True, "can_retry": True})
        result = self.convert_handler.converter.validate_data(yaml_docs)
        self.assertFalse(result["result"])
        self.assertIn("开启自动跳过后，不允许再配置可重试", str(result["message"]))

    def test_validate_service_activity_config_ignore_error_with_auto_retry(self):
        """开启自动跳过后配置自动重试(auto_retry.enable=True)应校验失败"""
        yaml_docs = self._build_yaml_docs(
            {"ignore_error": True, "auto_retry": {"enable": True, "interval": 0, "times": 1}}
        )
        result = self.convert_handler.converter.validate_data(yaml_docs)
        self.assertFalse(result["result"])
        self.assertIn("开启自动跳过后，不允许再配置可重试", str(result["message"]))

    def test_validate_service_activity_config_ignore_error_without_retry(self):
        """开启自动跳过后显式关闭可重试(can_retry=False)应通过校验"""
        yaml_docs = self._build_yaml_docs({"ignore_error": True, "can_retry": False})
        result = self.convert_handler.converter.validate_data(yaml_docs)
        self.assertTrue(result["result"], msg=result.get("message"))

    def test_validate_service_activity_config_three_enabled(self):
        """自动跳过 + 自动重试 + 超时控制 三个同时开启应校验失败"""
        yaml_docs = self._build_yaml_docs(
            {
                "ignore_error": True,
                "auto_retry": {"enable": True, "interval": 0, "times": 1},
                "timeout_config": {"enable": True, "seconds": 10, "action": "forced_fail"},
            }
        )
        result = self.convert_handler.converter.validate_data(yaml_docs)
        self.assertFalse(result["result"])
        self.assertIn("不能同时开启两个或两个以上", str(result["message"]))

    def test_validate_service_activity_config_can_retry_type_error(self):
        """can_retry 为非布尔类型应校验失败"""
        yaml_docs = self._build_yaml_docs({"can_retry": "yes"})
        result = self.convert_handler.converter.validate_data(yaml_docs)
        self.assertFalse(result["result"])
        self.assertIn("必须为布尔类型", str(result["message"]))

    def test_validate_service_activity_config_can_skip_type_error(self):
        """can_skip 为非布尔类型应校验失败"""
        yaml_docs = self._build_yaml_docs({"can_skip": 1})
        result = self.convert_handler.converter.validate_data(yaml_docs)
        self.assertFalse(result["result"])
        self.assertIn("必须为布尔类型", str(result["message"]))

    def _get_reconverted_activity(self, yaml_docs):
        """跑完整 reconvert 流程，返回其中 ServiceActivity 节点的原始流程树数据

        注意：reconvert 最后会调用 replace_all_id 重新生成所有节点 id，
        因此不能按 YAML 中的原始 id 取值，只能按节点类型定位。
        """
        reconvert_result = self.convert_handler.reconvert(yaml_docs)
        self.assertTrue(reconvert_result["result"], msg=reconvert_result.get("message"))
        templates = reconvert_result["data"]["templates"]
        template = next(iter(templates.values()))
        activities = template["tree"]["activities"]
        return next(activity for activity in activities.values() if activity["type"] == "ServiceActivity")

    def test_reconvert_uses_raw_field_names(self):
        """reconvert 后节点里只应保留原始字段名，不应残留映射后名"""
        yaml_docs = self._build_yaml_docs({"ignore_error": True, "can_retry": False, "can_skip": True})
        activity = self._get_reconverted_activity(yaml_docs)
        # 最终流程树只应有原始字段名
        self.assertIn("error_ignorable", activity)
        self.assertIn("retryable", activity)
        self.assertIn("skippable", activity)
        # 不应残留映射后字段名
        self.assertNotIn("ignore_error", activity)
        self.assertNotIn("can_retry", activity)
        self.assertNotIn("can_skip", activity)
        # 值正确映射
        self.assertTrue(activity["error_ignorable"])
        self.assertFalse(activity["retryable"])
        self.assertTrue(activity["skippable"])

    def test_convert_node_covers_all_node_types(self):
        """导出时所有节点类型都不应因 NODE_DEFAULT_FIELD_VALUE 缺 key 而 KeyError"""
        converter = self.convert_handler.converter
        param_constants = {"component_inputs": {}, "component_outputs": {}}
        for node_type, fields in converter.NODE_NECESSARY_FIELDS.items():
            node = {field: None for field in fields}
            node["type"] = node_type
            node["id"] = "n1"
            node["name"] = ""
            if node_type == "ServiceActivity":
                node["component"] = {"code": "bk_display", "data": {}, "version": "1.0"}
            if node_type == "SubProcess":
                # constants 不在 NODE_NECESSARY_FIELDS 中，但 _convert_node 的 SubProcess 分支会读取
                node["constants"] = {}
            if node_type in ("ExclusiveGateway", "ConditionalParallelGateway"):
                # conditions 在必要字段中，用 None 填充会导致实现里 conditions.values() 报错
                node["conditions"] = {}
            # 不应抛 KeyError
            converter._convert_node(node, param_constants)
