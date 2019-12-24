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

from copy import deepcopy

from django.test import TestCase

from pipeline.core.constants import PE

from pipeline_web.drawing_new.normalize import normalize_run, normalize_undo
from pipeline_web.drawing_new import acyclic
from pipeline_web.drawing_new.utils import add_flow_id_to_node_io
from pipeline_web.tests.drawing_new.data import pipeline_with_circle


class TestAcyclic(TestCase):
    def setUp(self):
        self.pipeline = deepcopy(pipeline_with_circle)

    def test_remove_self_flows(self):
        normalize_run(self.pipeline)
        self.assertEqual(acyclic.remove_self_edges(self.pipeline), {})
        edges = {
            'self_edge0': {
                PE.source: list(self.pipeline[PE.activities].keys())[0],
                PE.target: list(self.pipeline[PE.activities].keys())[0],
            },
            'self_edge1': {
                PE.source: list(self.pipeline[PE.activities].keys())[1],
                PE.target: list(self.pipeline[PE.activities].keys())[1],
            }
        }
        self.pipeline[PE.flows].update(edges)
        add_flow_id_to_node_io(list(self.pipeline[PE.activities].values())[0], 'self_edge0', PE.incoming)
        add_flow_id_to_node_io(list(self.pipeline[PE.activities].values())[0], 'self_edge0', PE.outgoing)
        add_flow_id_to_node_io(list(self.pipeline[PE.activities].values())[1], 'self_edge1', PE.incoming)
        add_flow_id_to_node_io(list(self.pipeline[PE.activities].values())[1], 'self_edge1', PE.outgoing)
        self.assertEqual(acyclic.remove_self_edges(self.pipeline), edges)
        normalize_undo(self.pipeline)
        self.assertEqual(self.pipeline, pipeline_with_circle)

    def test_insert_self_edges(self):
        edges = {
            'self_edge0': {
                PE.source: list(self.pipeline[PE.activities].keys())[0],
                PE.target: list(self.pipeline[PE.activities].keys())[0],
            },
            'self_edge2': {
                PE.source: list(self.pipeline[PE.activities].keys())[1],
                PE.target: list(self.pipeline[PE.activities].keys())[1],
            }
        }
        normalize_run(self.pipeline)
        acyclic.insert_self_edges(self.pipeline, edges)
        normalize_undo(self.pipeline)
        edges.update(self.pipeline[PE.flows])
        self.assertEqual(self.pipeline[PE.flows], edges)

    def test_acyclic_run(self):
        normalize_run(self.pipeline)
        reversed_flows = acyclic.acyclic_run(self.pipeline)
        assert_data = deepcopy(pipeline_with_circle)
        assert_flow = assert_data[PE.flows]['line77a6cd587ff8476e75354c1d9469']
        assert_flows = {
            'line77a6cd587ff8476e75354c1d9469': deepcopy(assert_flow)
        }
        assert_data[PE.activities][assert_flow[PE.target]].update({
            PE.incoming: ['linede15c52c74c1f5f566450d2c975a'],
            PE.outgoing: ['line8602a85ef7e511765b77bc9f05e0', 'line77a6cd587ff8476e75354c1d9469']
        })
        assert_data[PE.activities][assert_flow[PE.source]].update({
            PE.incoming: ['line7ac5fc7341c9ccbf773e9ca0c9cf', 'line77a6cd587ff8476e75354c1d9469'],
            PE.outgoing: ''
        })
        assert_flow.update({
            PE.source: assert_flow[PE.target],
            PE.target: assert_flow[PE.source]
        })
        self.assertEqual(reversed_flows, assert_flows)
        normalize_undo(self.pipeline)
        self.assertEqual(self.pipeline, assert_data)

    def test_acyclic_undo(self):
        normalize_run(self.pipeline)
        reversed_flows = acyclic.acyclic_run(self.pipeline)
        acyclic.acyclic_undo(self.pipeline, reversed_flows)
        normalize_undo(self.pipeline)
        self.assertEqual(self.pipeline, pipeline_with_circle)
