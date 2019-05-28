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
from pipeline.component_framework.library import ComponentLibrary
from pipeline.component_framework.models import ComponentModel
from pipeline.exceptions import ComponentNotExistException


class TestRegistry(TestCase):
    def setUp(self):
        class NewTestService(Service):
            pass

        class NewTestComponent(Component):
            name = 'name'
            code = 'new_test_component'
            bound_service = NewTestService
            form = 'form path'

        self.component = NewTestComponent

    def tearDown(self):
        ComponentModel.objects.all().delete()
        ComponentLibrary.components = {}

    def test_component(self):
        class TestService(Service):
            pass

        class TestComponent(Component):
            name = 'name'
            code = 'code'
            bound_service = TestService
            form = 'form path'

        self.assertEqual(ComponentLibrary.components['code'], TestComponent)

    def test_get_component(self):
        class TestService(Service):
            pass

        class TestComponent(Component):
            name = 'name'
            code = 'code'
            bound_service = TestService
            form = 'form path'

            def clean_execute_data(self, context):
                pass

            def outputs_format(self):
                pass

        self.assertEqual(ComponentLibrary.get_component('code', {}).__class__, TestComponent)

    def test_args_new(self):
        component = ComponentLibrary(self.component.code)
        self.assertEqual(component, self.component)

    def test_kwargs_new(self):
        component = ComponentLibrary(component_code=self.component.code)
        self.assertEqual(component, self.component)

    def test_new_not_exist(self):
        self.assertRaises(ComponentNotExistException, ComponentLibrary, 'not_exist')

    def test_new_no_pass_code(self):
        self.assertRaises(ValueError, ComponentLibrary)
