# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
from django.test import TestCase
from pipeline.core.data import base, context
from pipeline import exceptions


class TestContext(TestCase):
    def setUp(self):
        act_outputs = {
            'act_id_1': {
                'output_1': 'gk_1_1',
                'output_2': 'gk_1_2'
            },
            'act_id_2': {
                'output_1': 'gk_2_1'
            }
        }
        self.context = context.Context(act_outputs)

        class Activity(object):
            pass

        act_1 = Activity()
        act_1.id = 'act_id_1'
        data_1 = base.DataObject({})
        data_1.set_outputs('output_1', 'value_1_1')
        data_1.set_outputs('output_2', 'value_1_2')
        act_1.data = data_1
        self.act_1 = act_1

        act_2 = Activity()
        act_2.id = 'act_id_2'
        data_2 = base.DataObject({})
        data_2.set_outputs('output_1', 'value_2_1')
        data_2.set_outputs('output_2', 'value_2_2')
        data_2.set_outputs('output_3', 'value_2_3')
        act_2.data = data_2
        self.act_2 = act_2

        act_3 = Activity()
        act_3.id = 'act_id_3'
        data_3 = base.DataObject({})
        data_3.set_outputs('output_1', 'value_3_1')
        data_3.set_outputs('output_2', 'value_3_2')
        data_3.set_outputs('output_3', 'value_3_3')
        act_3.data = data_3
        self.act_3 = act_3

    def test_extract_output(self):
        self.context.extract_output(self.act_1)
        self.assertEqual(self.context.variables, {'gk_1_1': 'value_1_1', 'gk_1_2': 'value_1_2'})
        self.context.extract_output(self.act_2)
        self.assertEqual(self.context.variables, {'gk_1_1': 'value_1_1', 'gk_1_2': 'value_1_2', 'gk_2_1': 'value_2_1'})
        self.context.extract_output(self.act_3)
        self.assertEqual(self.context.variables, {'gk_1_1': 'value_1_1', 'gk_1_2': 'value_1_2', 'gk_2_1': 'value_2_1'})

    def test_get(self):
        self.context.extract_output(self.act_1)
        self.assertEqual(self.context.get('gk_1_1'), 'value_1_1')
        self.assertRaises(exceptions.ReferenceNotExistError, self.context.get, 'key_not_exist')

    def test_set_global_var(self):
        self.context.set_global_var('key', 'test_val')
        self.assertEqual(self.context.get('key'), 'test_val')

    def test_mark_as_output(self):
        self.context.mark_as_output('key')
        self.assertEqual(self.context._output_key, set(['key']))

    def test_output(self):
        class MockPipeline(object):
            def __init__(self, data):
                self.data = data
        pipeline = MockPipeline(base.DataObject({}))
        self.context.mark_as_output('gk_1_1')
        self.context.mark_as_output('gk_1_2')
        self.context.extract_output(self.act_1)
        self.context.write_output(pipeline)
        self.assertEqual(pipeline.data.get_outputs(), {'gk_1_1': 'value_1_1', 'gk_1_2': 'value_1_2'})


class TestOutputRef(TestCase):
    def setUp(self):
        act_outputs = {
            'act_id_1': {
                'output_1': 'gk_1_1',
                'output_2': 'gk_1_2'
            },
            'act_id_2': {
                'output_1': 'gk_2_1'
            }
        }
        self.context = context.Context(act_outputs)

        class Activity(object):
            pass

        act_1 = Activity()
        act_1.id = 'act_id_1'
        data_1 = base.DataObject({})
        data_1.set_outputs('output_1', 'value_1_1')
        data_1.set_outputs('output_2', 'value_1_2')
        act_1.data = data_1
        self.act_1 = act_1

    def test_value(self):
        ref = context.OutputRef('gk_1_1', self.context)
        self.context.extract_output(self.act_1)
        self.assertEqual(ref.value, 'value_1_1')
