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

from pipeline.builder.flow import NodeOutput


class NodeOutputTestCase(TestCase):
    def test_init(self):
        output = NodeOutput(type=NodeOutput.PLAIN, value="val", source_act="1", source_key="2")
        self.assertEqual(output.type, NodeOutput.PLAIN)
        self.assertEqual(output.value, None)
        self.assertEqual(output.source_act, "1")
        self.assertEqual(output.source_key, "2")

    def test_to_dict(self):
        output = NodeOutput(type=NodeOutput.PLAIN, value="val", source_act="1", source_key="2")
        d = output.to_dict()
        self.assertTrue(d, {"type": "plain", "value": "val", "source_act": "1", "source_key": "2"})
