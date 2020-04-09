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

from pipeline_web.drawing_new import acyclic
from pipeline_web.drawing_new.normalize import normalize_run, normalize_undo
from pipeline_web.drawing_new.rank import longest_path, feasible_tree
from pipeline_web.tests.drawing_new.data import pipeline_with_circle


class TestFeasibleTree(TestCase):
    def setUp(self):
        self.pipeline = deepcopy(pipeline_with_circle)
        normalize_run(self.pipeline)
        self.reversed_flows = acyclic.acyclic_run(self.pipeline)

    def test_feasible_tree_ranker(self):
        ranks = longest_path.longest_path_ranker(self.pipeline)
        ranks = feasible_tree.feasible_tree_ranker(self.pipeline, ranks)
        self.assertEqual(ranks, {
            'nodea4bb3693dfb8d99d2084cee2fb8b': 0,
            'nodeeb9b2a00e46adacd9f57720e8cca': -1,
            'node0dfa73e80b9bf40aa05f2442bb3d': -1,
            'node4149a8d446a7fc325b66a7ee4350': -2,
            'nodeaf2161961809a91ebb00db88c814': -3,
            'node402bea676e660fab4cc643afafc8': -4
        })

    def tearDown(self):
        acyclic.acyclic_undo(self.pipeline, self.reversed_flows)
        normalize_undo(self.pipeline)
