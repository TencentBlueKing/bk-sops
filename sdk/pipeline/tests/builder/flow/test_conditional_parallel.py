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

from pipeline.builder.flow.gateway import ConditionalParallelGateway
from pipeline.core.constants import PE


class ConditionalParallelGatewayTestCase(TestCase):
    def test_type(self):
        e = ConditionalParallelGateway()
        self.assertEqual(e.type(), PE.ConditionalParallelGateway)

    def test_init(self):
        e = ConditionalParallelGateway()
        self.assertEqual(len(e.id), 32)
        self.assertIsNone(e.name)
        self.assertEqual(e.outgoing, [])
        self.assertEqual(e.conditions, {})

        e = ConditionalParallelGateway(id="123", name="test_eg", outgoing=[1, 2, 3], conditions={0: "123"})
        self.assertEqual(e.id, "123")
        self.assertEqual(e.name, "test_eg")
        self.assertEqual(e.outgoing, [1, 2, 3])
        self.assertEqual(e.conditions, {0: "123"})

    def test_add_condition(self):
        e = ConditionalParallelGateway(id="123", name="test_eg", outgoing=[1, 2, 3], conditions={0: "123"})
        e.add_condition(1, "456")
        self.assertEqual(e.conditions, {0: "123", 1: "456"})

    def test_link_conditions_with(self):
        e = ConditionalParallelGateway(
            id="123", name="test_eg", outgoing=[1, 2, 3], conditions={0: "123", 1: "456", 2: "789"}
        )

        outgoing = ["abc", "def", "ghi"]
        conditions = e.link_conditions_with(outgoing)
        self.assertEqual(
            conditions, {"abc": {"evaluate": "123"}, "def": {"evaluate": "456"}, "ghi": {"evaluate": "789"}}
        )
