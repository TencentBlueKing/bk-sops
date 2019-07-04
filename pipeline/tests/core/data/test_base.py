# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
import unittest

from pipeline.core.data.base import DataObject
from pipeline.core.flow.activity import Activity
from pipeline import exceptions


class TestData(unittest.TestCase):

    def test_data_object(self):
        inputs = {'args': '1', 'kwargs': {'1': 1, '2': 2}}

        self.assertRaises(exceptions.DataTypeErrorException, DataObject, None)

        data_object = DataObject(inputs)
        self.assertIsInstance(data_object, DataObject)

        self.assertEqual(data_object.get_inputs(), inputs)
        self.assertEqual(data_object.get_outputs(), {})

        self.assertEqual(data_object.get_one_of_inputs('args'), '1')
        self.assertIsNone(data_object.get_one_of_outputs('args'))

        self.assertRaises(exceptions.DataTypeErrorException,
                          data_object.reset_outputs, None)
        self.assertTrue(data_object.reset_outputs({'a': str}))

