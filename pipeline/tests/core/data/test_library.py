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

from pipeline.core.data import library
from pipeline.core.data.context import Context
from pipeline.core.data.var import LazyVariable


class TestLibrary(TestCase):
    class VarIpPickerVariable(LazyVariable):
        code = 'ip'
        form = 'var.js'

        def get_value(self):
            return self.value

    def setUp(self):
        self.name = '${ip}'
        self.info = {
            'source_tag': u'var_ip_picker.ip_picker',
            'custom_type': 'ip',
            'type': 'lazy',
            'value': {
                u'var_ip_custom_value': u'1.1.1.11.1',
                u'var_ip_method': u'custom',
                u'var_ip_tree': u''
            }
        }
        self.context = Context(self.name)
        self.pipeline_data = {
            'language': 'zh-cn',
            'task_id': 78,
            'biz_cc_name': u'UTC',
            'task_name': u'20180918175615',
            'executor': u'username',
            'operator': u'username',
            'biz_cc_id': 0
        }
        self.code = 'ip'

    def test_get_var_class(self):
        cls = library.VariableLibrary
        variable_class = cls.get_var_class(self.info['custom_type'])
        self.assertEqual(variable_class.code, self.code)

    def test_get_var(self):
        cls = library.VariableLibrary
        variable = cls.get_var(self.code, self.name, self.info["value"], self.context, self.pipeline_data)
        self.assertEqual(variable.name, self.name)
        self.assertEqual(variable.value, self.info["value"])
