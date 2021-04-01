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

from pipeline.builder.flow import Var


class VarTestCase(TestCase):
    def test_init(self):
        var = Var(type="test_type", value="test_value", custom_type="source_tag")
        self.assertEqual(var.type, "test_type")
        self.assertEqual(var.value, "test_value")
        self.assertEqual(var.custom_type, "source_tag")

    def test_to_dict(self):
        splice_var = Var(type=Var.SPLICE, value="val", custom_type="source_tag")
        plain_var = Var(type=Var.PLAIN, value="val", custom_type="source_tag")
        lazy_var = Var(type=Var.LAZY, value="val", custom_type="source_tag")

        self.assertEqual(splice_var.to_dict(), {"type": Var.SPLICE, "value": "val"})
        self.assertEqual(plain_var.to_dict(), {"type": Var.PLAIN, "value": "val"})
        self.assertEqual(lazy_var.to_dict(), {"type": Var.LAZY, "value": "val", "custom_type": "source_tag"})
