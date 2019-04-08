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

from pipeline.core.flow.activity import Service
from pipeline.component_framework.component import Component
from pipeline.core.data.var import PlainVariable
from pipeline.core.data.base import DataObject
from pipeline.exceptions import ComponentDataLackException
from pipeline.component_framework.models import ComponentModel
from pipeline.component_framework.library import ComponentLibrary


class TestComponent(TestCase):
    def setUp(self):
        class CCUpdateHostModuleService(Service):
            def execute(self, data, parent_data):
                pass

            def outputs(self):
                return [
                    self.OutputItem(name='key_1', key='key_1', type='int'),
                    self.OutputItem(name='key_2', key='key_2', type='str')
                ]

            def outputs_format(self):
                pass

        class CCUpdateHostModuleComponent(Component):
            name = u'修改主机所属模块'
            bound_service = CCUpdateHostModuleService
            code = 'cc_update_module'
            form = 'form path'

        self.service = CCUpdateHostModuleService
        self.component = CCUpdateHostModuleComponent

    def tearDown(self):
        ComponentModel.objects.all().delete()
        ComponentLibrary.components = {}

    def test_init(self):
        self.component({})

    def test_outputs_format(self):
        outputs_format = self.component({}).outputs_format()
        self.assertEqual(outputs_format, [
            {'name': 'key_1', 'key': 'key_1', 'type': 'int'},
            {'name': 'key_2', 'key': 'key_2', 'type': 'str'}
        ])

    def test_clean_execution_data(self):
        data = {'test': 'test'}
        data_after_clean = self.component(data).clean_execute_data(None)
        self.assertEqual(data, data_after_clean)

    def test_service(self):
        service = self.component({}).service()
        self.assertIsInstance(service, self.service)

    def test_data_for_execution(self):
        v1 = PlainVariable(name='key_1', value='value_1')
        v2 = PlainVariable(name='key_2', value='value_2')
        data = {
            'key_1': {'value': v1},
            'key_2': {'value': v2}
        }
        component = self.component(data)
        execution_data = component.data_for_execution({}, {})
        self.assertIsInstance(execution_data, DataObject)
        self.assertEqual(execution_data.get_inputs(), {
            'key_1': v1,
            'key_2': v2
        })

    def test_data_for_execution_lack_of_inputs(self):
        PlainVariable(name='key_1', value='value_1')
        data = {
            'key_1': None,
            'key_2': None
        }
        component = self.component(data)
        self.assertRaises(ComponentDataLackException, execution_data=component.data_for_execution, args=[None, None])
