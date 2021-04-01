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

from pipeline.core.data import base, context, var


class TestPlainVariable(TestCase):
    def test_get(self):
        pv = var.PlainVariable("name", "value")
        self.assertEqual(pv.get(), "value")


class TestSpliceVariable(TestCase):
    def setUp(self):
        act_outputs = {
            "act_id_1": {"output_1": "${gk_1_1}", "output_2": "${gk_1_2}"},
            "act_id_2": {"output_1": "${gk_2_1}"},
        }
        self.context = context.Context(act_outputs)

        class Activity(object):
            pass

        act_1 = Activity()
        act_1.id = "act_id_1"
        data_1 = base.DataObject({})
        data_1.set_outputs("output_1", "value_1_1")
        data_1.set_outputs("output_2", "value_1_2")
        act_1.data = data_1
        self.act_1 = act_1

        self.context_1 = context.Context({})
        self.context_1.variables["${grandparent_key}"] = "grandparent_value"

    def test_get(self):
        sv = var.SpliceVariable(name="name", value="${gk_1_1}_${gk_1_2}_${key_not_exist}", context=self.context)
        self.context.extract_output(self.act_1)
        self.assertEqual(sv.get(), "value_1_1_value_1_2_${key_not_exist}")

    def test_object_get(self):
        value = {
            "key1": ["${gk_1_1}_test1", "${gk_1_2}_test2"],
            "key2": {"key2_1": "${gk_1_1}_${gk_1_2}_${key_not_exist}"},
        }
        sv = var.SpliceVariable(name="name", value=value, context=self.context)
        self.context.extract_output(self.act_1)
        test_value = {
            "key1": ["value_1_1_test1", "value_1_2_test2"],
            "key2": {"key2_1": "value_1_1_value_1_2_${key_not_exist}"},
        }
        self.assertEqual(sv.get(), test_value)
