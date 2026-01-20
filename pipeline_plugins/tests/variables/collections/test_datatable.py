# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
from django.test import TestCase

from pipeline_plugins.variables.collections.datatable import DataTable, DataTableValue


class DataTableTestCase(TestCase):
    def test_datatable_value_init(self):
        data = [{"col1": "val1", "col2": "val2"}, {"col1": "val3", "col2": "val4"}]
        dt_val = DataTableValue(data)

        self.assertEqual(dt_val.col1, ["val1", "val3"])
        self.assertEqual(dt_val.col2, ["val2", "val4"])
        self.assertEqual(dt_val.flat__col1, "val1\nval3")
        self.assertEqual(dt_val.flat__col2, "val2\nval4")
        self.assertTrue("DataTable with" in str(dt_val))

    def test_datatable_value_init_with_json_string(self):
        data = '[{"col1": "val1"}]'
        dt_val = DataTableValue(data)
        self.assertEqual(dt_val.col1, ["val1"])

    def test_datatable_value_init_error(self):
        # Test json load error
        data = "{invalid_json"
        # initialization will fail at for loop because string is iterable but item (char) has no items()
        with self.assertRaises(AttributeError):
            DataTableValue(data)

    def test_datatable_get_value(self):
        data = [{"col1": "val1"}]
        dt = DataTable(name="test", value=data, context={}, pipeline_data={})
        val = dt.get_value()
        self.assertIsInstance(val, DataTableValue)
        self.assertEqual(val.col1, ["val1"])
