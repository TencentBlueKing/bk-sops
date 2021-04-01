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

from pipeline.engine.utils import Stack


class TestStack(TestCase):
    def test_push(self):
        stack = Stack()
        self.assertEqual(stack, [])
        stack.push(1)
        stack.push(2)
        self.assertEqual(stack, [1, 2])

    def test_pop(self):
        stack = Stack()
        self.assertRaises(IndexError, stack.pop)
        stack.push(1)
        stack.push(2)
        r = stack.pop()
        self.assertEqual(r, 2)
        self.assertEqual(stack, [1])
        r = stack.pop()
        self.assertEqual(r, 1)
        self.assertEqual(stack, [])

    def test_top(self):
        stack = Stack()
        self.assertRaises(IndexError, stack.top)
        stack.push(1)
        self.assertEqual(stack.top(), 1)
        self.assertEqual(stack, [1])
        stack.push(2)
        self.assertEqual(stack.top(), 2)
        self.assertEqual(stack, [1, 2])
