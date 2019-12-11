# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from __future__ import absolute_import

from django.test import TestCase

from pipeline.core.constants import PE

from pipeline_web.drawing_new.order import order


class TestOrder(TestCase):
    def setUp(self):
        self.pipeline = {
            'all_nodes': {
                'node0': {
                    PE.id: 'node0',
                    PE.incoming: '',
                    PE.outgoing: ['flow0', 'flow1', 'flow2']
                },
                'node1': {
                    PE.id: 'node1',
                    PE.incoming: 'flow0',
                    PE.outgoing: ['flow3', 'flow4']
                },
                'node2': {
                    PE.id: 'node2',
                    PE.incoming: 'flow1',
                    PE.outgoing: ['flow5', 'flow6', 'flow7']
                },
                'node3': {
                    PE.id: 'node3',
                    PE.incoming: 'flow2',
                    PE.outgoing: ['flow8', 'flow9', 'flow10']
                },
                'node4': {
                    PE.id: 'node4',
                    PE.incoming: ['flow3', 'flow5', 'flow8'],
                    PE.outgoing: ''
                },
                'node5': {
                    PE.id: 'node5',
                    PE.incoming: ['flow4'],
                    PE.outgoing: ''
                },
                'node6': {
                    PE.id: 'node6',
                    PE.incoming: ['flow6'],
                    PE.outgoing: ''
                },
                'node7': {
                    PE.id: 'node7',
                    PE.incoming: ['flow7', 'flow9'],
                    PE.outgoing: ''
                },
                'node8': {
                    PE.id: 'node8',
                    PE.incoming: ['flow10'],
                    PE.outgoing: ''
                }
            },
            'flows': {
                'flow0': {
                    PE.id: 'flow0',
                    PE.source: 'node0',
                    PE.target: 'node1'
                },
                'flow1': {
                    PE.id: 'flow1',
                    PE.source: 'node0',
                    PE.target: 'node2'
                },
                'flow2': {
                    PE.id: 'flow2',
                    PE.source: 'node0',
                    PE.target: 'node3'
                },
                'flow3': {
                    PE.id: 'flow3',
                    PE.source: 'node1',
                    PE.target: 'node4'
                },
                'flow4': {
                    PE.id: 'flow4',
                    PE.source: 'node1',
                    PE.target: 'node5'
                },
                'flow5': {
                    PE.id: 'flow5',
                    PE.source: 'node2',
                    PE.target: 'node4'
                },
                'flow6': {
                    PE.id: 'flow6',
                    PE.source: 'node2',
                    PE.target: 'node6'
                },
                'flow7': {
                    PE.id: 'flow7',
                    PE.source: 'node2',
                    PE.target: 'node7'
                },
                'flow8': {
                    PE.id: 'flow8',
                    PE.source: 'node3',
                    PE.target: 'node4'
                },
                'flow9': {
                    PE.id: 'flow9',
                    PE.source: 'node3',
                    PE.target: 'node7'
                },
                'flow10': {
                    PE.id: 'flow10',
                    PE.source: 'node3',
                    PE.target: 'node8'
                }
            }
        }
        self.ranks = {
            'node0': 0,
            'node1': 1,
            'node2': 1,
            'node3': 1,
            'node4': 2,
            'node5': 2,
            'node6': 2,
            'node7': 2,
            'node8': 2
        }

    def test_init_order(self):
        orders = order.init_order(self.pipeline, self.ranks)
        self.assertEqual(orders, {
            0: ['node0'],
            1: ['node1', 'node2', 'node3'],
            2: ['node4', 'node5', 'node6', 'node7', 'node8']
        })

    def test_crossing_count(self):
        orders = {
            0: ['node0'],
            1: ['node1', 'node2', 'node3'],
            2: ['node4', 'node5', 'node6', 'node7', 'node8']
        }
        self.assertEqual(order.crossing_count(self.pipeline, orders), 4)

    def test_sort_layer(self):
        layer_order = ['a', 'b', 'c', 'd', 'e', 'f']
        weight = [3, 6, 2, 1, 5, 4]
        self.assertEqual(order.sort_layer(layer_order, weight), ['d', 'c', 'a', 'f', 'e', 'b'])
        layer_order = ['a', 'b']
        weight = [-1, -1]
        self.assertEqual(order.sort_layer(layer_order, weight), ['a', 'b'])
        layer_order = ['a', 'b', 'c', 'd', 'e', 'f']
        weight = [3, -1, 2, -1, 5, 4]
        self.assertEqual(order.sort_layer(layer_order, weight), ['c', 'b', 'a', 'd', 'f', 'e'])

    def test_median_value(self):
        refer_layer_orders = ['node1', 'node2', 'node3', 'node4']
        refer_nodes = ['node1']
        self.assertEqual(order.median_value(refer_nodes, refer_layer_orders), 0)
        refer_nodes = ['node1', 'node4']
        self.assertEqual(order.median_value(refer_nodes, refer_layer_orders), 1.5)
        refer_nodes = ['node1', 'node4', 'node2']
        self.assertEqual(order.median_value(refer_nodes, refer_layer_orders), 1)

    def test_refer_node_ids(self):
        self.assertEqual(order.refer_node_ids(self.pipeline, 'node1', PE.outgoing), ['node4', 'node5'])
        self.assertEqual(order.refer_node_ids(self.pipeline, 'node4', PE.incoming), ['node1', 'node2', 'node3'])

    def test_ordering(self):
        best_orders = {
            0: ['node0'],
            1: ['node1', 'node2', 'node3'],
            2: ['node5', 'node4', 'node6', 'node7', 'node8']
        }
        self.assertEqual(order.ordering(self.pipeline, self.ranks), best_orders)
