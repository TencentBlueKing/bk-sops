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
        with open("{}/test_complicated_data.json".format(self.dir_path)) as infile:
            self.original_data = json.load(infile)
        with open("{}/test_complicated_yaml_data.yaml".format(self.dir_path)) as infile:
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
                        {"type": "SubProcess", "id": "sub", "name": "sub", "template_id": 1001, "next": ["end"]},
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
        with open("{}/test_yaml_data.yaml".format(self.dir_path)) as infile:
            yaml_docs = list(yaml.safe_load_all(infile))
        with open("{}/test_original_data.json".format(self.dir_path)) as infile:
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
