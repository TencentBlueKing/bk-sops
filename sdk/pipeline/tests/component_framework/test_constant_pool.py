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

from pipeline import exceptions
from pipeline.component_framework.constant import ConstantPool
from pipeline.utils.utils import has_circle


class TestConstantPool(TestCase):
    def setUp(self):
        data = {
            "${key_a}": {"value": "haha"},
            "${key_b}": {"value": "str_${key_a}"},
            "${key_c}": {"value": "str_${key_b}"},
        }
        resolved_data = {
            "${key_a}": {"value": "haha"},
            "${key_b}": {"value": "str_haha"},
            "${key_c}": {"value": "str_str_haha"},
        }
        pool = ConstantPool(data)
        self.pool = pool
        self.resolved_data = resolved_data

    def test_resolve(self):
        self.pool.resolve()
        self.assertEqual(self.pool.pool, self.resolved_data)

    def test_has_circle(self):
        g1 = {
            "a": ["b", "d"],
            "b": ["f", "c"],
            "c": ["a", "d", "e"],
            "d": ["e"],
            "e": [],
            "f": ["c"],
            "g": ["f", "h"],
            "h": ["f", "j"],
            "i": ["h"],
            "j": ["i"],
        }

        g2 = {"a": [], "b": ["a"], "c": ["b", "a"], "d": []}

        g3 = {
            "a": ["b", "d"],
            "b": ["f", "c"],
            "c": ["d", "e"],
            "d": ["e"],
            "e": [],
            "f": ["c"],
            "g": ["f", "h"],
            "h": ["f", "j"],
            "i": ["h"],
            "j": ["i"],
        }

        g4 = {
            "a": ["b", "d"],
            "b": ["f", "c"],
            "c": ["d", "e"],
            "d": ["e"],
            "e": [],
            "f": ["c"],
            "g": ["f", "h"],
            "h": ["f", "j"],
            "i": ["h"],
            "j": [],
        }

        g5 = {"a": ["a"]}

        g6 = {"a": ["b"], "b": ["c"], "c": ["a"]}

        self.assertTrue(has_circle(g1)[0])
        self.assertFalse(has_circle(g2)[0])
        self.assertTrue(has_circle(g3)[0])
        self.assertFalse(has_circle(g4)[0])
        self.assertTrue(has_circle(g5)[0])
        self.assertTrue(has_circle(g6)[0])

    def test_resolve_value(self):
        self.assertEqual(self.pool.resolve_value("value_${key_c}"), "value_str_str_haha")
        self.assertEqual(self.pool.resolve_value("value_${key_a}_${key_d}"), "value_haha_${key_d}")

    def test_resolve_constant(self):
        self.assertEqual(self.pool.resolve_constant("${key_a}"), "haha")
        self.assertRaises(exceptions.ConstantNotExistException, self.pool.resolve_constant, "${key_d}")
