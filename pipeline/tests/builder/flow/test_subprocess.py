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

from pipeline.core.constants import PE
from pipeline.builder.flow import SubProcess


class SubProcessTestCase(TestCase):
    def test_init(self):
        subproc = SubProcess('template_id')
        self.assertEqual(subproc.start, 'template_id')
        self.assertEqual(subproc.params, {})
        self.assertIsNone(subproc.data)

        subproc = SubProcess(
            start='template_id',
            data={'data_key': 'data_val'},
            params={'1': '2'})
        self.assertEqual(subproc.start, 'template_id')
        self.assertEqual(subproc.data, {'data_key': 'data_val'})
        self.assertEqual(subproc.params, {'1': '2'})

    def test_type(self):
        subproc = SubProcess('template_id')
        self.assertEqual(subproc.type(), PE.SubProcess)
