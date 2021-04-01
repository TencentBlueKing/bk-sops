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

from pipeline.core.flow.base import SequenceFlow, SequenceFlowCollection
from pipeline.exceptions import InvalidOperationException


class Obj(object):
    pass


class TestFlowCollection(TestCase):
    def test_sequence_flow_collection(self):
        flow1 = SequenceFlow("1", Obj(), Obj())
        flow2 = SequenceFlow("4", Obj(), Obj())
        flow3 = SequenceFlow("7", Obj(), Obj())
        flows = [flow1, flow2, flow3]
        flow_dict = {flow1.id: flow1, flow2.id: flow2, flow3.id: flow3}
        collection = SequenceFlowCollection(*flows)
        self.assertEqual(flows, collection.flows)
        self.assertEqual(flow_dict, collection.flow_dict)

    def test_get_flow(self):
        flow1 = SequenceFlow("1", Obj(), Obj())
        flow2 = SequenceFlow("4", Obj(), Obj())
        flow3 = SequenceFlow("7", Obj(), Obj())
        flows = [flow1, flow2, flow3]
        collection = SequenceFlowCollection(*flows)
        self.assertEqual(flow1, collection.get_flow(flow1.id))
        self.assertEqual(flow2, collection.get_flow(flow2.id))
        self.assertEqual(flow3, collection.get_flow(flow3.id))

    def test_unique_one(self):
        flow1 = SequenceFlow("1", Obj(), Obj())
        flow2 = SequenceFlow("4", Obj(), Obj())
        flow3 = SequenceFlow("7", Obj(), Obj())
        flows = [flow1, flow2, flow3]
        not_unique_collection = SequenceFlowCollection(*flows)
        unique_collection = SequenceFlowCollection(flow1)
        self.assertEqual(flow1, unique_collection.unique_one())
        self.assertRaises(InvalidOperationException, not_unique_collection.unique_one)

    def test_is_empty(self):
        flow1 = SequenceFlow("1", Obj(), Obj())
        flow2 = SequenceFlow("4", Obj(), Obj())
        flow3 = SequenceFlow("7", Obj(), Obj())
        flows = [flow1, flow2, flow3]
        not_empty_collection = SequenceFlowCollection(*flows)
        empty_collection = SequenceFlowCollection()
        self.assertTrue(empty_collection.is_empty())
        self.assertFalse(not_empty_collection.is_empty())

    def test_add_flow(self):
        flow1 = SequenceFlow("1", Obj(), Obj())
        flow2 = SequenceFlow("4", Obj(), Obj())
        flow3 = SequenceFlow("7", Obj(), Obj())
        flow4 = SequenceFlow("10", Obj(), Obj())
        flows = [flow1, flow2, flow3]
        flows_after_added = [flow1, flow2, flow3, flow4]
        flow_dict_after_added = {flow1.id: flow1, flow2.id: flow2, flow3.id: flow3, flow4.id: flow4}
        collection = SequenceFlowCollection(*flows)
        collection.add_flow(flow4)
        self.assertEqual(flows_after_added, collection.flows)
        self.assertEqual(flow_dict_after_added, collection.flow_dict)

    def test_all_target(self):
        targets = [Obj(), Obj(), Obj()]
        flow1 = SequenceFlow("1", Obj(), targets[0])
        flow2 = SequenceFlow("4", Obj(), targets[1])
        flow3 = SequenceFlow("7", Obj(), targets[2])
        flows = [flow1, flow2, flow3]
        collection = SequenceFlowCollection(*flows)
        self.assertEqual(targets, collection.all_target_node())

    def test_all_source(self):
        sources = [Obj(), Obj(), Obj()]
        flow1 = SequenceFlow("1", sources[0], Obj())
        flow2 = SequenceFlow("4", sources[1], Obj())
        flow3 = SequenceFlow("7", sources[2], Obj())
        flows = [flow1, flow2, flow3]
        collection = SequenceFlowCollection(*flows)
        self.assertEqual(sources, collection.all_source_node())
