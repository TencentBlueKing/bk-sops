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

from pipeline.core.flow.base import SequenceFlow
from pipeline.core.flow.gateway import Condition, ConditionalParallelGateway, ParallelGateway
from pipeline.exceptions import ConditionExhaustedException, InvalidOperationException
from pipeline.tests.mock import *  # noqa


class ConditionalParallelGatewayTestCase(TestCase):
    def setUp(self):
        self.id = "id"
        self.name = "name"
        self.data = "data"
        self.converge_gateway_id = "converge_gateway_id"
        self.conditions = [1, 2, 3]

    def test_init(self):
        cpg_1 = ConditionalParallelGateway(id=self.id, converge_gateway_id=self.converge_gateway_id)
        self.assertEqual(cpg_1.id, self.id)
        self.assertEqual(cpg_1.converge_gateway_id, self.converge_gateway_id)
        self.assertEqual(cpg_1.conditions, [])
        self.assertIsNone(cpg_1.name)
        self.assertIsNone(cpg_1.data)

        cpg_2 = ConditionalParallelGateway(
            id=self.id,
            converge_gateway_id=self.converge_gateway_id,
            conditions=self.conditions,
            name=self.name,
            data=self.data,
        )
        self.assertEqual(cpg_2.id, self.id)
        self.assertEqual(cpg_2.converge_gateway_id, self.converge_gateway_id)
        self.assertEqual(cpg_2.conditions, self.conditions)
        self.assertEqual(cpg_2.name, self.name)
        self.assertEqual(cpg_2.data, self.data)

    def test_add_condition(self):
        cpg = ConditionalParallelGateway(id=self.id, converge_gateway_id=self.converge_gateway_id)
        cpg.add_condition("condition_1")
        cpg.add_condition("condition_2")
        self.assertEqual(cpg.conditions, ["condition_1", "condition_2"])

    def test_targets_meet_condition__normal(self):
        node_1 = ParallelGateway(id="1", converge_gateway_id="cvg")
        node_2 = ParallelGateway(id="2", converge_gateway_id="cvg")
        node_3 = ParallelGateway(id="3", converge_gateway_id="cvg")
        node_4 = ParallelGateway(id="4", converge_gateway_id="cvg")
        condition_1 = Condition(evaluate="1 == 1", sequence_flow=SequenceFlow(id=self.id, source=node_1, target=node_1))
        condition_2 = Condition(evaluate="1 == 0", sequence_flow=SequenceFlow(id=self.id, source=node_2, target=node_2))
        condition_3 = Condition(evaluate="1 == 1", sequence_flow=SequenceFlow(id=self.id, source=node_3, target=node_3))
        condition_4 = Condition(evaluate="1 == 0", sequence_flow=SequenceFlow(id=self.id, source=node_4, target=node_4))
        cpg = ConditionalParallelGateway(
            id=self.id,
            converge_gateway_id=self.converge_gateway_id,
            conditions=[condition_1, condition_2, condition_3, condition_4],
        )

        targets = cpg.targets_meet_condition({})
        self.assertEqual(targets, [node_1, node_3])

    def test_targets_meet_condition__raise_exhausted(self):
        condition_1 = Condition(evaluate="1 == 0", sequence_flow=SequenceFlow(id=self.id, source=None, target=None))
        condition_2 = Condition(evaluate="1 == 0", sequence_flow=SequenceFlow(id=self.id, source=None, target=None))
        condition_3 = Condition(evaluate="1 == 0", sequence_flow=SequenceFlow(id=self.id, source=None, target=None))
        condition_4 = Condition(evaluate="1 == 0", sequence_flow=SequenceFlow(id=self.id, source=None, target=None))
        cpg = ConditionalParallelGateway(
            id=self.id,
            converge_gateway_id=self.converge_gateway_id,
            conditions=[condition_1, condition_2, condition_3, condition_4],
        )

        self.assertRaises(ConditionExhaustedException, cpg.targets_meet_condition, {})

    def test_next(self):
        cpg = ConditionalParallelGateway(id=self.id, converge_gateway_id=self.converge_gateway_id)
        self.assertRaises(InvalidOperationException, cpg.next)

    def test_skip(self):
        cpg = ConditionalParallelGateway(id=self.id, converge_gateway_id=self.converge_gateway_id)
        self.assertRaises(InvalidOperationException, cpg.skip)
