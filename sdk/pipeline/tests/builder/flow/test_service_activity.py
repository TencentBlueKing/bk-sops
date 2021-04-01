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

from pipeline.builder.flow import ServiceActivity
from pipeline.builder.flow.data import Var
from pipeline.core.constants import PE


class ServiceActivityTestCase(TestCase):
    def test_init(self):
        act = ServiceActivity()
        self.assertIsNotNone(act.component)
        self.assertIsNone(act.component.code)
        self.assertEqual(act.component.inputs, {})

        act = ServiceActivity(component_code="test")
        self.assertEqual(act.component.code, "test")

    def test_type(self):
        act = ServiceActivity()
        self.assertEqual(act.type(), PE.ServiceActivity)

    def test_component_dict(self):
        act = ServiceActivity()
        act.component.code = "http"
        act.component.inputs.parent_data = Var(type=Var.SPLICE, value="${parent_data}")
        act.component.inputs.val = Var(type=Var.PLAIN, value="${val}")
        act.component.inputs.lazy_val = Var(type=Var.LAZY, value="${val}", custom_type="test_tag")

        cd = act.component_dict()
        self.assertEqual(
            cd,
            {
                "code": "http",
                "inputs": {
                    "parent_data": {"type": "splice", "value": "${parent_data}"},
                    "val": {"type": "plain", "value": "${val}"},
                    "lazy_val": {"type": "lazy", "value": "${val}", "custom_type": "test_tag"},
                },
            },
        )
