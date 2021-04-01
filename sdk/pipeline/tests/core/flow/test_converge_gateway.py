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

from pipeline.core.flow.base import FlowNode, SequenceFlow
from pipeline.core.flow.gateway import ConvergeGateway, Gateway, ParallelGateway


class TestConvergeGateway(TestCase):
    def test_converge_gateway(self):
        gw_id = "1"
        cvg_gateway = ConvergeGateway(gw_id)
        self.assertTrue(isinstance(cvg_gateway, FlowNode))
        self.assertTrue(isinstance(cvg_gateway, Gateway))

    def test_next(self):
        cvg_gateway = ConvergeGateway("1")
        parallel_gateway = ParallelGateway("2", "cvg")
        out_flow = SequenceFlow("flow", cvg_gateway, parallel_gateway)
        cvg_gateway.outgoing.add_flow(out_flow)
        parallel_gateway.incoming.add_flow(out_flow)
        self.assertEqual(parallel_gateway, cvg_gateway.next())
