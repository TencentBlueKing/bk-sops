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

from pipeline_plugins.cmdb_ip_picker.utils import format_condition_value


class FormatConditionVlaueTestCase(TestCase):
    def test__normal(self):
        self.assertEqual(format_condition_value(["111", "222"]), list({"111", "222"}))
        self.assertEqual(format_condition_value(["111", "222\n333"]), list({"111", "222", "333"}))
        self.assertEqual(format_condition_value(["", "222\n", " 333  "]), list({"222", "333"}))

    def test__number_case(self):
        self.assertEqual(set(format_condition_value([111, 222, 333])), set([111, 222, 333]))
