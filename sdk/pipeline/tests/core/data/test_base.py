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

import jsonschema
import ujson as json
from django.test import TestCase

from pipeline import exceptions
from pipeline.core.data.base import DataObject
from pipeline.core.data.schemas import BASE_PARAM
from pipeline.utils.collections import FancyDict


class TestData(TestCase):
    def test_data_object(self):
        inputs = {"args": "1", "kwargs": {"1": 1, "2": 2}}

        self.assertRaises(exceptions.DataTypeErrorException, DataObject, None)

        data_object = DataObject(inputs)
        self.assertIsInstance(data_object, DataObject)
        self.assertIsInstance(data_object.inputs, FancyDict)
        self.assertIsInstance(data_object.outputs, FancyDict)

        self.assertEqual(data_object.get_inputs(), inputs)
        self.assertEqual(data_object.get_outputs(), {})

        self.assertEqual(data_object.get_one_of_inputs("args"), "1")
        self.assertEqual(data_object.inputs.args, "1")
        self.assertIsNone(data_object.get_one_of_outputs("args"))

        self.assertRaises(exceptions.DataTypeErrorException, data_object.reset_outputs, None)
        self.assertTrue(data_object.reset_outputs({"a": str}))
        self.assertEqual(data_object.outputs.a, str)

        data_object.update_outputs({"args": "1", "kwargs": {"1": 1, "2": 2}})
        self.assertEqual(data_object.get_outputs(), {"a": str, "args": "1", "kwargs": {"1": 1, "2": 2}})
        self.assertEqual(jsonschema.validate(json.loads(data_object.serializer()), BASE_PARAM), None)

    def test_inputs_copy(self):
        inputs = {"args": "1", "kwargs": {"1": 1, "2": 2}}
        data_object = DataObject(inputs=inputs)
        inputs_copy = data_object.inputs_copy()
        self.assertIsInstance(inputs_copy, FancyDict)
        self.assertEqual(inputs_copy, inputs)
        self.assertFalse(inputs is inputs_copy)

    def test_outputs_copy(self):
        outputs = {"args": "1", "kwargs": {"1": 1, "2": 2}}
        data_object = DataObject(inputs={}, outputs=outputs)
        outputs_copy = data_object.outputs_copy()
        self.assertIsInstance(outputs_copy, FancyDict)
        self.assertEqual(outputs_copy, outputs)
        self.assertFalse(outputs_copy is outputs)
