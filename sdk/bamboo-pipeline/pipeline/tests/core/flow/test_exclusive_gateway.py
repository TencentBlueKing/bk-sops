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

from django.test import TestCase

from pipeline.core.flow.base import FlowNode, SequenceFlow
from pipeline.core.flow.gateway import Condition, ExclusiveGateway, Gateway, ParallelGateway
from pipeline.exceptions import ConditionExhaustedException, EvaluationException


class TestExclusiveGateway(TestCase):
    def setUp(self):
        ex_gateway1 = ExclusiveGateway(id="1")
        next_node1 = ParallelGateway(id="1", converge_gateway_id="cvg")
        next_node2 = ParallelGateway(id="2", converge_gateway_id="cvg")
        flow1 = SequenceFlow("flow1", ex_gateway1, next_node1)
        flow2 = SequenceFlow("flow2", ex_gateway1, next_node2)
        condition1 = Condition("a == 1", flow1)
        condition2 = Condition("a != 1", flow2)
        ex_gateway1.add_condition(condition1)
        ex_gateway1.add_condition(condition2)
        ex_gateway1.outgoing.add_flow(flow1)
        ex_gateway1.outgoing.add_flow(flow2)
        next_node1.incoming.add_flow(flow1)
        next_node2.incoming.add_flow(flow2)

        self.gateway_for_test_determine = ex_gateway1

        ex_gateway2 = ExclusiveGateway(id="2")
        next_node3 = ParallelGateway(id="3", converge_gateway_id="cvg")
        next_node4 = ParallelGateway(id="4", converge_gateway_id="cvg")
        next_node5 = ParallelGateway(id="5", converge_gateway_id="cvg")
        flow3 = SequenceFlow("flow3", ex_gateway2, next_node3)
        flow4 = SequenceFlow("flow4", ex_gateway2, next_node4)
        flow5 = SequenceFlow("flow5", ex_gateway2, next_node5, is_default=True)
        condition3 = Condition("a == 1", flow3)
        condition4 = Condition("a != 1", flow4)
        ex_gateway2.add_condition(condition3)
        ex_gateway2.add_condition(condition4)
        ex_gateway2.outgoing.add_flow(flow3)
        ex_gateway2.outgoing.add_flow(flow4)
        ex_gateway2.outgoing.add_flow(flow5)
        next_node3.incoming.add_flow(flow3)
        next_node4.incoming.add_flow(flow4)
        next_node5.incoming.add_flow(flow5)

        self.gateway_for_test_next = ex_gateway2

        self.nodes = [next_node1, next_node2, next_node3, next_node4, next_node5]

    def test_exclusive_gateway(self):
        gw_id = "1"
        conditions = [Condition(None, None), Condition(None, None)]
        ex_gateway = ExclusiveGateway(id=gw_id, conditions=conditions)
        self.assertTrue(isinstance(ex_gateway, FlowNode))
        self.assertTrue(isinstance(ex_gateway, Gateway))
        self.assertEqual(conditions, ex_gateway.conditions)

    def test_add_condition(self):
        ex_gateway = ExclusiveGateway(id="1")
        flow1 = SequenceFlow("flow1", ex_gateway, None)
        self.assertEqual([], ex_gateway.conditions)
        ex_gateway.add_condition(flow1)
        self.assertEqual([flow1], ex_gateway.conditions)

    def test_determine_next_flow_success(self):
        flow1 = self.gateway_for_test_determine.outgoing.flows[0]
        flow2 = self.gateway_for_test_determine.outgoing.flows[1]
        data1 = {"a": 1}
        data2 = {"a": 2}
        self.assertEqual(flow1, self.gateway_for_test_determine._determine_next_flow_with_boolrule(data1))
        self.assertEqual(flow2, self.gateway_for_test_determine._determine_next_flow_with_boolrule(data2))

    def test_determine_next_flow_exhausted(self):
        self.gateway_for_test_determine.conditions[1].evaluate = "a > 1"
        data = {"a": -1}
        self.assertIsNone(self.gateway_for_test_determine._determine_next_flow_with_boolrule(data))

    def test_determine_next_evaluation_exception(self):
        self.gateway_for_test_determine.conditions[0].evaluate = "c == 1"
        data = {"a": 1}
        self.assertRaises(EvaluationException, self.gateway_for_test_determine._determine_next_flow_with_boolrule, data)

    def test_next_success(self):
        node = self.gateway_for_test_next.outgoing.flows[1].target
        data = {"a": 2}
        self.assertEqual(node, self.gateway_for_test_next.next(data))

    def test_next_exhausted(self):
        node = self.gateway_for_test_next.outgoing.flows[2].target
        self.gateway_for_test_next.conditions[1].evaluate = "a > 1"
        data = {"a": 0}
        self.assertEqual(node, self.gateway_for_test_next.next(data))
        self.gateway_for_test_next.outgoing.flows[2].is_default = False
        self.assertRaises(ConditionExhaustedException, self.gateway_for_test_next.next, data)

    def test_next_raise(self):
        origin = self.gateway_for_test_next.conditions[1].evaluate
        self.gateway_for_test_next.conditions[1].evaluate = "b > 1"
        data = {"a": 0}
        self.assertRaises(EvaluationException, self.gateway_for_test_next.next, data)
        self.gateway_for_test_next.conditions[1].evaluate = origin
