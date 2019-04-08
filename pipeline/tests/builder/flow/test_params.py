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

from pipeline.builder.flow import Params, Var


class DataTestCase(TestCase):

    def test_init(self):
        params = Params()
        self.assertEqual(params.params, {})

    def test_to_dict(self):
        params = Params()

        params.params['${constant_1}'] = Var(type=Var.PLAIN, value='value_1')
        params.params['${constant_2}'] = {'type': 'plain', 'value': 'value_2'}

        d = params.to_dict()

        self.assertEqual(d, {'${constant_1}': {'type': 'plain', 'value': 'value_1'},
                             '${constant_2}': {'type': 'plain', 'value': 'value_2'}})
