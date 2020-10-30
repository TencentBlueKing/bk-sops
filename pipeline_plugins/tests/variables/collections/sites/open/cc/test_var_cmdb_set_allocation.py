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

from pipeline_plugins.variables.collections.sites.open.cc import VarCmdbSetAllocation


class VarCmdbSetAllocationTestCase(TestCase):
    def setUp(self):
        self.name = "name_token"
        self.value = {
            "separator": ";",
            "data": [
                {
                    "__module": [{"key": "module_a", "value": ["1.1.1.1"]}],
                    "bk_set_name": "test",
                    "bk_set_desc": "description",
                    "test_attr": "test_attr",
                },
                {
                    "__module": [
                        {"key": "module_b", "value": ["2.2.2.2"]},
                        {"key": "module_c", "value": ["1.2.3.4", "2.3.4.5"]},
                    ],
                    "bk_set_name": "test2",
                    "bk_set_desc": "description2",
                    "test_attr": "test_attr2",
                },
            ],
        }
        self.context = {}
        self.pipeline_data = {}

    def test_get_value_with_separator(self):
        set_allocation = VarCmdbSetAllocation(self.name, self.value, self.context, self.pipeline_data)
        set_detail_data = set_allocation.get_value()

        self.assertEqual(set_detail_data.set_count, 2)
        self.assertEqual(set_detail_data.flat__bk_set_name, "test;test2")
        self.assertEqual(
            set_detail_data._module, [{"module_a": "1.1.1.1"}, {"module_b": "2.2.2.2", "module_c": "1.2.3.4;2.3.4.5"}]
        )
        self.assertEqual(set_detail_data.flat__verbose_ip_list, "1.1.1.1;2.2.2.2;1.2.3.4;2.3.4.5")
        self.assertEqual(
            set_detail_data.flat__verbose_ip_module_list, "test>module_a;test2>module_b;test2>module_c;test2>module_c"
        )

    def test_get_value_without_separator(self):
        self.value.pop("separator")
        set_allocation = VarCmdbSetAllocation(self.name, self.value, self.context, self.pipeline_data)
        set_detail_data = set_allocation.get_value()

        self.assertEqual(set_detail_data.set_count, 2)
        self.assertEqual(set_detail_data.flat__bk_set_name, "test,test2")
        self.assertEqual(
            set_detail_data._module, [{"module_a": "1.1.1.1"}, {"module_b": "2.2.2.2", "module_c": "1.2.3.4,2.3.4.5"}]
        )
        self.assertEqual(set_detail_data.flat__verbose_ip_list, "1.1.1.1,2.2.2.2,1.2.3.4,2.3.4.5")
        self.assertEqual(
            set_detail_data.flat__verbose_ip_module_list, "test>module_a,test2>module_b,test2>module_c,test2>module_c"
        )
