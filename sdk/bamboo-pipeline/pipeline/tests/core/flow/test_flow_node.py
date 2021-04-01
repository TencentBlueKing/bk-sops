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

from pipeline.core.flow.base import FlowElement, FlowNode, SequenceFlowCollection


class MockNode(FlowNode):
    def next(self):
        raise Exception()


class TestFlowNode(TestCase):
    def test_flow_node(self):
        node_id = "1"
        flow_node = MockNode(node_id)
        self.assertTrue(isinstance(flow_node, FlowElement))
        self.assertEqual(node_id, flow_node.id)
        default_collection_node = MockNode(node_id)
        self.assertTrue(isinstance(default_collection_node.incoming, SequenceFlowCollection))
        self.assertTrue(isinstance(default_collection_node.outgoing, SequenceFlowCollection))

    def test_next_exec_is_retry(self):
        node_id = "1"
        flow_node = MockNode(node_id)
        flow_node.next_exec_is_retry()
        self.assertTrue(hasattr(flow_node, FlowNode.ON_RETRY))

    def test_on_retry(self):
        node_id = "1"
        flow_node = MockNode(node_id)
        flow_node.next_exec_is_retry()
        self.assertTrue(flow_node.on_retry())

    def test_retry_at_current_exec(self):
        node_id = "1"
        flow_node = MockNode(node_id)
        flow_node.next_exec_is_retry()
        self.assertTrue(flow_node.on_retry())
        flow_node.retry_at_current_exec()
        self.assertFalse(flow_node.on_retry())
