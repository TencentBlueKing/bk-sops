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
import json

from django.test import TestCase

from bamboo_engine.eri import (
    NodeType,
    ServiceActivity,
    SubProcess,
    ExclusiveGateway,
    ParallelGateway,
    ConditionalParallelGateway,
    ConvergeGateway,
    EmptyStartEvent,
    EmptyEndEvent,
    ExecutableEndEvent,
)

from pipeline.eri.imp.node import NodeMixin
from pipeline.eri.models import Node as DBNode


class ProcessMixinTestCase(TestCase):
    def setUp(self):
        self.mixin = NodeMixin()

    def test_get_node(self):
        nodes = {
            "n1": {
                "id": "n1",
                "type": NodeType.ServiceActivity.value,
                "targets": {"f1": "t1"},
                "root_pipeline_id": "root",
                "parent_pipeline_id": "parent",
                "can_skip": True,
                "can_retry": True,
                "code": "test_code",
                "version": "legacy",
                "timeout": None,
                "error_ignorable": True,
            },
            "n2": {
                "id": "n2",
                "type": NodeType.SubProcess.value,
                "targets": {"f1": "t1"},
                "root_pipeline_id": "root",
                "parent_pipeline_id": "parent",
                "start_event_id": "s1",
                "can_skip": True,
                "can_retry": True,
            },
            "n3": {
                "id": "n3",
                "type": NodeType.ExclusiveGateway.value,
                "targets": {"f1": "t1", "f2": "t2"},
                "root_pipeline_id": "root",
                "parent_pipeline_id": "parent",
                "can_skip": True,
                "can_retry": True,
                "conditions": [
                    {"name": "c1", "evaluation": "${k} == 1", "target_id": "t1", "flow_id": "f1"},
                    {"name": "c2", "evaluation": "${k} == 2", "target_id": "t2", "flow_id": "f2"},
                ],
            },
            "n4": {
                "id": "n4",
                "type": NodeType.ParallelGateway.value,
                "targets": {"f1": "t1", "f2": "t2"},
                "root_pipeline_id": "root",
                "parent_pipeline_id": "parent",
                "converge_gateway_id": "c1",
                "can_skip": True,
                "can_retry": True,
            },
            "n5": {
                "id": "n5",
                "type": NodeType.ConditionalParallelGateway.value,
                "targets": {"f1": "t1", "f2": "t2"},
                "root_pipeline_id": "root",
                "parent_pipeline_id": "parent",
                "can_skip": True,
                "can_retry": True,
                "conditions": [
                    {"name": "c1", "evaluation": "${k} == 1", "target_id": "t1", "flow_id": "f1"},
                    {"name": "c2", "evaluation": "${k} == 2", "target_id": "t2", "flow_id": "f2"},
                ],
                "converge_gateway_id": "c1",
            },
            "n6": {
                "id": "n6",
                "type": NodeType.ConvergeGateway.value,
                "targets": {"f1": "t1"},
                "root_pipeline_id": "root",
                "parent_pipeline_id": "parent",
                "can_skip": True,
                "can_retry": True,
            },
            "n7": {
                "id": "n7",
                "type": NodeType.EmptyStartEvent.value,
                "targets": {"f1": "t1"},
                "root_pipeline_id": "root",
                "parent_pipeline_id": "parent",
                "can_skip": True,
                "can_retry": True,
            },
            "n8": {
                "id": "n8",
                "type": NodeType.EmptyEndEvent.value,
                "targets": {"f1": "t1"},
                "root_pipeline_id": "root",
                "parent_pipeline_id": "parent",
                "can_skip": True,
                "can_retry": True,
            },
            "n9": {
                "id": "n9",
                "type": NodeType.ExecutableEndEvent.value,
                "targets": {"f1": "t1"},
                "root_pipeline_id": "root",
                "parent_pipeline_id": "parent",
                "code": "",
                "can_skip": True,
                "can_retry": True,
            },
        }
        for node_id, detail in nodes.items():
            DBNode.objects.create(node_id=node_id, detail=json.dumps(detail))

        node = self.mixin.get_node("n1")
        self.assertTrue(isinstance(node, ServiceActivity))
        self.assertEqual(node.id, "n1")
        self.assertEqual(node.type, NodeType.ServiceActivity)
        self.assertEqual(node.target_flows, ["f1"])
        self.assertEqual(node.target_nodes, ["t1"])
        self.assertEqual(node.targets, {"f1": "t1"})
        self.assertEqual(node.root_pipeline_id, "root")
        self.assertEqual(node.parent_pipeline_id, "parent")
        self.assertEqual(node.can_skip, True)
        self.assertEqual(node.can_retry, True)
        self.assertEqual(node.code, "test_code")
        self.assertEqual(node.version, "legacy")
        self.assertEqual(node.timeout, None)
        self.assertEqual(node.error_ignorable, True)

        node = self.mixin.get_node("n2")
        self.assertTrue(isinstance(node, SubProcess))
        self.assertEqual(node.id, "n2")
        self.assertEqual(node.type, NodeType.SubProcess)
        self.assertEqual(node.target_flows, ["f1"])
        self.assertEqual(node.target_nodes, ["t1"])
        self.assertEqual(node.targets, {"f1": "t1"})
        self.assertEqual(node.root_pipeline_id, "root")
        self.assertEqual(node.parent_pipeline_id, "parent")
        self.assertEqual(node.can_skip, True)
        self.assertEqual(node.can_retry, True)
        self.assertEqual(node.start_event_id, "s1")

        node = self.mixin.get_node("n3")
        self.assertTrue(isinstance(node, ExclusiveGateway))
        self.assertEqual(node.id, "n3")
        self.assertEqual(node.type, NodeType.ExclusiveGateway)
        self.assertEqual(node.target_flows, ["f1", "f2"])
        self.assertEqual(node.target_nodes, ["t1", "t2"])
        self.assertEqual(node.targets, {"f1": "t1", "f2": "t2"})
        self.assertEqual(node.root_pipeline_id, "root")
        self.assertEqual(node.parent_pipeline_id, "parent")
        self.assertEqual(node.can_skip, True)
        self.assertEqual(node.can_retry, True)
        self.assertEqual(
            [(c.name, c.evaluation, c.target_id, c.flow_id) for c in node.conditions],
            [("c1", "${k} == 1", "t1", "f1"), ("c2", "${k} == 2", "t2", "f2")],
        )

        node = self.mixin.get_node("n4")
        self.assertTrue(isinstance(node, ParallelGateway))
        self.assertEqual(node.id, "n4")
        self.assertEqual(node.type, NodeType.ParallelGateway)
        self.assertEqual(node.target_flows, ["f1", "f2"])
        self.assertEqual(node.target_nodes, ["t1", "t2"])
        self.assertEqual(node.targets, {"f1": "t1", "f2": "t2"})
        self.assertEqual(node.root_pipeline_id, "root")
        self.assertEqual(node.parent_pipeline_id, "parent")
        self.assertEqual(node.can_skip, True)
        self.assertEqual(node.can_retry, True)
        self.assertEqual(node.converge_gateway_id, "c1")

        node = self.mixin.get_node("n5")
        self.assertTrue(isinstance(node, ConditionalParallelGateway))
        self.assertEqual(node.id, "n5")
        self.assertEqual(node.type, NodeType.ConditionalParallelGateway)
        self.assertEqual(node.target_flows, ["f1", "f2"])
        self.assertEqual(node.target_nodes, ["t1", "t2"])
        self.assertEqual(node.targets, {"f1": "t1", "f2": "t2"})
        self.assertEqual(node.root_pipeline_id, "root")
        self.assertEqual(node.parent_pipeline_id, "parent")
        self.assertEqual(node.can_skip, True)
        self.assertEqual(node.can_retry, True)
        self.assertEqual(
            [(c.name, c.evaluation, c.target_id, c.flow_id) for c in node.conditions],
            [("c1", "${k} == 1", "t1", "f1"), ("c2", "${k} == 2", "t2", "f2")],
        )
        self.assertEqual(node.converge_gateway_id, "c1")

        node = self.mixin.get_node("n6")
        self.assertTrue(isinstance(node, ConvergeGateway))
        self.assertEqual(node.id, "n6")
        self.assertEqual(node.type, NodeType.ConvergeGateway)
        self.assertEqual(node.target_flows, ["f1"])
        self.assertEqual(node.target_nodes, ["t1"])
        self.assertEqual(node.targets, {"f1": "t1"})
        self.assertEqual(node.root_pipeline_id, "root")
        self.assertEqual(node.parent_pipeline_id, "parent")
        self.assertEqual(node.can_skip, True)
        self.assertEqual(node.can_retry, True)

        node = self.mixin.get_node("n7")
        self.assertTrue(isinstance(node, EmptyStartEvent))
        self.assertEqual(node.id, "n7")
        self.assertEqual(node.type, NodeType.EmptyStartEvent)
        self.assertEqual(node.target_flows, ["f1"])
        self.assertEqual(node.target_nodes, ["t1"])
        self.assertEqual(node.targets, {"f1": "t1"})
        self.assertEqual(node.root_pipeline_id, "root")
        self.assertEqual(node.parent_pipeline_id, "parent")
        self.assertEqual(node.can_skip, True)
        self.assertEqual(node.can_retry, True)

        node = self.mixin.get_node("n8")
        self.assertTrue(isinstance(node, EmptyEndEvent))
        self.assertEqual(node.id, "n8")
        self.assertEqual(node.type, NodeType.EmptyEndEvent)
        self.assertEqual(node.target_flows, ["f1"])
        self.assertEqual(node.target_nodes, ["t1"])
        self.assertEqual(node.targets, {"f1": "t1"})
        self.assertEqual(node.root_pipeline_id, "root")
        self.assertEqual(node.parent_pipeline_id, "parent")
        self.assertEqual(node.can_skip, True)
        self.assertEqual(node.can_retry, True)

        node = self.mixin.get_node("n9")
        self.assertTrue(isinstance(node, ExecutableEndEvent))
        self.assertEqual(node.id, "n9")
        self.assertEqual(node.type, NodeType.ExecutableEndEvent)
        self.assertEqual(node.target_flows, ["f1"])
        self.assertEqual(node.target_nodes, ["t1"])
        self.assertEqual(node.targets, {"f1": "t1"})
        self.assertEqual(node.root_pipeline_id, "root")
        self.assertEqual(node.parent_pipeline_id, "parent")
        self.assertEqual(node.can_skip, True)
        self.assertEqual(node.can_retry, True)
        self.assertEqual(node.code, "")
