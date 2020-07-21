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

from datetime import datetime
from mock import MagicMock, patch

from django.test import TestCase

from pipeline_plugins.variables.collections.common import CurrentTime


class CurrentTimeTestCase(TestCase):
    def setUp(self):
        self.name = "name_token"
        self.time = datetime(2020, 7, 17, 20, 27, 4)
        self.context = {}
        self.pipeline_data = {}

    def test_generate_time_format(self):
        generate_time_format_func = CurrentTime._generate_time_format
        needed_units_cases = [
            ["year", "month", "day", "hour", "minute", "second"],
            ["year", "month", "day"],
            ["hour", "minute", "second"],
            ["month", "day", "minute", "second"],
            ["day", "hour", "minute"],
        ]
        output_formats = ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%H:%M:%S", "%m-%d %M:%S", "%d %H:%M"]
        for case_idx in range(len(needed_units_cases)):
            needed_units = needed_units_cases[case_idx]
            output_format = output_formats[case_idx]
            self.assertEqual(generate_time_format_func(needed_units), output_format)

    def test_get_value_with_all_units(self):
        value = {"time_unit": ["year", "month", "day", "hour", "minute", "second"], "time_zone": "Asia/Shanghai"}
        current_time = CurrentTime(self.name, value, self.context, self.pipeline_data)
        mock_current_time = MagicMock()
        mock_current_time.now.return_value = self.time
        with patch("pipeline_plugins.variables.collections.common.datetime.datetime", mock_current_time):
            output_time = current_time.get_value()
        self.assertEqual(output_time, "2020-07-17 20:27:04")

    def test_get_value_without_year_and_second_units(self):
        value = {"time_unit": ["month", "day", "hour", "minute"], "time_zone": "Asia/Shanghai"}
        current_time = CurrentTime(self.name, value, self.context, self.pipeline_data)
        mock_current_time = MagicMock()
        mock_current_time.now.return_value = self.time
        with patch("pipeline_plugins.variables.collections.common.datetime.datetime", mock_current_time):
            output_time = current_time.get_value()
        self.assertEqual(output_time, "07-17 20:27")
