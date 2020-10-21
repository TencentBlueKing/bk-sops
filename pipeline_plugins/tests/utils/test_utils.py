# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from django.test import TestCase

from pipeline_plugins.components.utils import chunk_table_data


class UtilsTestCase(TestCase):
    def test_chunk_table_data(self):
        success_column_input = {"gamedb": "1,2,3", "gamedr": "4", "logdb": "4,5,6"}
        has_int_success_column_input = {"gamedb": "1,2,3", "gamedr": 4, "logdb": "4,5,6"}
        failed_column_input = {"gamedb": "1,2", "gamedr": "4", "logdb": "4,5,6"}
        break_line = ","
        expect_column = [
            {"gamedb": "1", "gamedr": "4", "logdb": "4"},
            {"gamedb": "2", "gamedr": "4", "logdb": "5"},
            {"gamedb": "3", "gamedr": "4", "logdb": "6"},
        ]
        has_int_expect_column = [
            {"gamedb": "1", "gamedr": 4, "logdb": "4"},
            {"gamedb": "2", "gamedr": 4, "logdb": "5"},
            {"gamedb": "3", "gamedr": 4, "logdb": "6"},
        ]
        success_actual_column = chunk_table_data(success_column_input, break_line)
        has_int_success_actual_column = chunk_table_data(has_int_success_column_input, break_line)
        failed_actual_column = chunk_table_data(failed_column_input, break_line)
        self.assertEqual(expect_column, success_actual_column["data"])
        self.assertEqual(has_int_expect_column, has_int_success_actual_column["data"])
        self.assertEqual([], failed_actual_column["data"])
        self.assertFalse(failed_actual_column["result"])
