# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from django.test import TestCase

from pipeline.core.data.context import Context
from pipeline.core.data.converter import get_variable
from pipeline import exceptions


class TestConverter(TestCase):
    def setUp(self):
        self.key = 'bk_timing'
        self.info = {
            'type': 'plain',
            'value': '1'
        }
        self.context = Context({})
        self.pipeline_data = {
            'language': 'zh-cn',
            'task_id': 63,
            'biz_cc_name': u'UTC',
            'task_name': u'20180918165807',
            'executor': u'username',
            'operator': u'username',
            'biz_cc_id': 81
        }

    def test_get_variable(self):
        variable = get_variable(self.key, self.info, self.context, self.pipeline_data)
        self.assertEqual(variable.name, 'bk_timing')
        self.assertEqual(variable.value, '1')

        self.info['type'] = 'splice'
        variable1 = get_variable(self.key, self.info, self.context, self.pipeline_data)
        self.assertEqual(variable1.name, 'bk_timing')
        self.assertEqual(variable1.value, '1')
        self.assertEqual(variable1._refs, {})

        self.key = '${ip}'
        self.info = {
            'source_tag': u'var_ip_picker.ip_picker',
            'type': 'lazy',
            'value': {
                u'var_ip_custom_value': u'1.1.1.11.1',
                u'var_ip_method': u'custom',
                u'var_ip_tree': u''
            }
        }
        self.context = Context(self.key)
        self.pipeline_data = {
            'language': 'zh-cn',
            'task_id': 78,
            'biz_cc_name': u'UTC',
            'task_name': u'20180918175615',
            'executor': u'username',
            'operator': u'username',
            'biz_cc_id': 0
        }

        variable2 = get_variable(self.key, self.info, self.context, self.pipeline_data)
        self.assertEqual(variable2.name, '${ip}')
        self.assertEqual(variable2.value, self.info["value"])
        self.assertEqual(variable2._refs, {})
        self.assertEqual(variable2.code, 'var_ip_picker')

        self.info["type"] = 'exception'
        self.assertRaises(exceptions.DataTypeErrorException, get_variable, self.key, self.info, self.context,
                          self.pipeline_data)
