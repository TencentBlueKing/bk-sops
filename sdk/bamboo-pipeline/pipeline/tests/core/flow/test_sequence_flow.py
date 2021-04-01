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

from pipeline.core.data.base import DataObject
from pipeline.core.flow.activity import ServiceActivity
from pipeline.core.flow.base import FlowElement, SequenceFlow


class TestSequenceFlow(TestCase):
    def test_sequence_flow(self):
        flow_id = "1"
        source = ServiceActivity(id="1", service=None, data=DataObject({}))
        target = ServiceActivity(id="2", service=None, data=DataObject({}))
        flow = SequenceFlow(flow_id, source, target)
        self.assertTrue(isinstance(flow, FlowElement))
        self.assertEqual(flow_id, flow.id)
        self.assertEqual(source, flow.source)
        self.assertEqual(target, flow.target)
        self.assertEqual(False, flow.is_default)
