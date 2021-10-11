# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
from django.test import TestCase

from gcloud.utils.algorithms import topology_sort


class TestAlgorithmsTestCase(TestCase):
    def test__topology_sort(self):
        relations = {"a": ["b", "c", "d", "f"], "g": ["a", "h"], "e": ["b", "f", "g"]}
        orders = topology_sort(relations)
        self.assertTrue(all([orders.index("a") > orders.index(pre_node) for pre_node in ["b", "c", "d", "f"]]))
        self.assertTrue(all([orders.index("g") > orders.index(pre_node) for pre_node in ["a", "h"]]))
        self.assertTrue(all([orders.index("e") > orders.index(pre_node) for pre_node in ["g"]]))
