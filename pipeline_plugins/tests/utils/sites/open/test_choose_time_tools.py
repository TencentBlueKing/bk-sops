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
import mock
from django.test import TestCase

from pipeline_plugins.components.utils.sites.open.choose_time_tools import choose_time, get_end_time_by_duration


class ChooseTimeToolsTestCase(TestCase):
    def test_get_end_time_by_duration(self):
        start_time = "2023-01-01 10:00:00"
        duration = 60
        expected = "2023-01-01 11:00:00"
        self.assertEqual(get_end_time_by_duration(start_time, duration), expected)

    def test_choose_time(self):
        # Type 0: Manual input
        start_time = "2023-01-01 10:00:00"
        end_time = "2023-01-01 11:00:00"
        s, e = choose_time(0, start_time, end_time, 0)
        self.assertEqual(s, start_time)
        self.assertEqual(e, end_time)

        # Type 0: Invalid input
        with self.assertRaises(ValueError):
            choose_time(0, "invalid", "invalid", 0)

        # Type 1: Current time + duration
        with mock.patch("pipeline_plugins.components.utils.sites.open.choose_time_tools.time") as mock_time:
            mock_time.strftime.return_value = "2023-01-01 10:00:00"
            s, e = choose_time(1, "", "", 60)
            self.assertEqual(s, "2023-01-01 10:00:00")
            self.assertEqual(e, "2023-01-01 11:00:00")

        # Type 2: Start time + duration
        s, e = choose_time(2, "2023-01-01 10:00:00", "", 60)
        self.assertEqual(s, "2023-01-01 10:00:00")
        self.assertEqual(e, "2023-01-01 11:00:00")

        # Type 2: Invalid start time
        with self.assertRaises(ValueError):
            choose_time(2, "invalid", "", 60)
