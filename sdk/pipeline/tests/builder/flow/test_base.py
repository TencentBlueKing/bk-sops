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

from pipeline.builder.flow.base import Element


class TestElement(TestCase):
    def test_init(self):
        e1 = Element()
        self.assertEqual(len(e1.id), 32)
        self.assertIsNone(e1.name)
        self.assertListEqual(e1.outgoing, [])

        e2 = Element(id="id", name="name", outgoing=[1])
        self.assertEqual(e2.id, "id")
        self.assertEqual(e2.name, "name")
        self.assertEqual(e2.outgoing, [1])

    def test_extend(self):
        e1 = Element()
        e2 = Element()
        e3 = Element()

        ret = e1.extend(e2).extend(e3)
        self.assertEqual(ret, e3)
        self.assertEqual(e1.outgoing, [e2])
        self.assertEqual(e2.outgoing, [e3])

    def test_connect(self):
        e1 = Element()
        e2 = Element()

        ret = e1.connect(e2)
        self.assertEqual(ret, e1)
        self.assertEqual(ret.outgoing, [e2])

        e3 = Element()
        e4 = Element()
        e5 = Element()
        e6 = Element()

        ret = e3.connect(e4, e5, e6)
        self.assertEqual(ret, e3)
        self.assertEqual(e3.outgoing, [e4, e5, e6])

    def test_to(self):
        e1 = Element()
        e2 = Element()

        self.assertEqual(e1.to(e1), e1)
        self.assertEqual(e1.to(e2), e2)
        self.assertEqual(e2.to(e1), e1)

    def test_converge(self):
        e1 = Element()
        e2 = Element()
        e3 = Element()
        e4 = Element()
        e5 = Element()

        e1.connect(e2, e3, e4)
        ret = e1.converge(e5)
        self.assertEqual(ret, e5)
        self.assertEqual(e2.outgoing, [e5])
        self.assertEqual(e3.outgoing, [e5])
        self.assertEqual(e4.outgoing, [e5])

        e6 = Element()
        e7 = Element()
        e8 = Element()
        e9 = Element()
        e10 = Element()

        ret = e6.extend(e7).extend(e8).to(e6).extend(e9).to(e6).converge(e10)

        self.assertEqual(ret, e10)
        self.assertEqual(e6.outgoing, [e7, e9])
        self.assertEqual(e7.outgoing, [e8])
        self.assertEqual(e8.outgoing, [e10])
        self.assertEqual(e9.outgoing, [e10])

        e11 = Element()
        self.assertEqual(e11.tail(), e11)

    def test_type(self):
        e1 = Element()
        self.assertRaises(NotImplementedError, e1.type)
