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

from pipeline_web.constants import PWE
from pipeline_web.drawing_new import dummy


class TestDummy(TestCase):
    def setUp(self):
        self.node_id1 = 'node1'
        self.node_id2 = 'node2'
        self.flow_id = 'line1'
        self.pipeline = {
            'all_nodes': {
                self.node_id1: {
                    PWE.id: self.node_id1,
                    PWE.incoming: '',
                    PWE.outgoing: self.flow_id
                },
                self.node_id2: {
                    PWE.id: self.node_id2,
                    PWE.incoming: self.flow_id,
                    PWE.outgoing: ''
                }
            },
            PWE.flows: {
                self.flow_id: {
                    PWE.id: self.flow_id,
                    PWE.source: self.node_id1,
                    PWE.target: self.node_id2
                }
            }
        }
        self.pipeline_bak = deepcopy(self.pipeline)
        self.flows = deepcopy(self.pipeline[PWE.flows])
        self.ranks = {
            self.node_id1: -2,
            self.node_id2: 0
        }
        self.ranks_bak = deepcopy(self.ranks)

    def test_replace_long_path_with_dummy_nodes(self):
        self.real_flows_chain = dummy.replace_long_path_with_dummy(self.pipeline, self.ranks)
        self.assertEqual(self.real_flows_chain, self.flows)
        self.assertEqual(set(self.ranks.values()), {-2, -1, 0})
        self.assertNotEqual(self.pipeline['all_nodes'][self.node_id1][PWE.outgoing], self.flow_id)
        self.assertNotEqual(self.pipeline['all_nodes'][self.node_id2][PWE.incoming], self.flow_id)

        self.assertEqual(len(list(self.pipeline[PWE.flows].keys())), 2)

    def test_remove_dummy_nodes(self):
        self.real_flows_chain = dummy.replace_long_path_with_dummy(self.pipeline, self.ranks)
        dummy.remove_dummy(self.pipeline, self.real_flows_chain, dummy_nodes_included=[self.ranks])
        self.assertEqual(self.pipeline, self.pipeline_bak)
        self.assertEqual(self.ranks, self.ranks_bak)
