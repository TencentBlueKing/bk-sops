# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from django.test import TestCase

from pipeline.component_framework.component import Component
from pipeline.component_framework.constants import LEGACY_PLUGINS_VERSION
from pipeline.component_framework.library import ComponentLibrary
from pipeline.component_framework.models import ComponentModel
from pipeline.core.flow.activity import Service
from pipeline.exceptions import ComponentNotExistException


class TestRegistry(TestCase):
    def setUp(self):
        class NewTestService(Service):
            pass

        class NewTestComponent(Component):
            name = "name"
            code = "new_test_component"
            bound_service = NewTestService
            form = "form path"

        self.component = NewTestComponent

    def tearDown(self):
        ComponentModel.objects.all().delete()
        ComponentLibrary.components = {}

    def test_component(self):
        class TestService(Service):
            pass

        class TestComponent(Component):
            name = "name"
            code = "code"
            bound_service = TestService
            form = "form path"

        self.assertEqual(ComponentLibrary.components["code"][LEGACY_PLUGINS_VERSION], TestComponent)

    def test_get_component_class(self):
        class TestService(Service):
            pass

        class TestComponent(Component):
            name = "name"
            code = "code"
            bound_service = TestService
            form = "form path"

            def clean_execute_data(self, context):
                pass

            def outputs_format(self):
                pass

        class TestComponent2(Component):
            name = "name"
            code = "code_2"
            bound_service = TestService
            form = "form path"
            version = "1.0"

            def clean_execute_data(self, context):
                pass

            def outputs_format(self):
                pass

        self.assertEqual(ComponentLibrary.get_component_class("code"), TestComponent)
        self.assertRaises(ComponentNotExistException, ComponentLibrary.get_component_class, "code", "1.0")
        self.assertRaises(ComponentNotExistException, ComponentLibrary.get_component_class, "code2")
        self.assertEqual(ComponentLibrary.get_component_class("code_2", "1.0"), TestComponent2)

    def test_get_component__raise(self):
        self.assertRaises(ComponentNotExistException, ComponentLibrary.get_component, "c_not_exist", {})

    def test_args_new(self):
        component = ComponentLibrary(self.component.code)
        self.assertEqual(component, self.component)

    def test_get_component(self):
        class TestService(Service):
            pass

        class TestComponent(Component):
            name = "name"
            code = "code"
            bound_service = TestService
            form = "form path"

            def clean_execute_data(self, context):
                pass

            def outputs_format(self):
                pass

        self.assertEqual(ComponentLibrary.get_component("code", {}).__class__, TestComponent)

    def test_register_component(self):
        component_cls = "component_token"
        ComponentLibrary.register_component(component_code="code_1", version="1", component_cls=component_cls)
        ComponentLibrary.register_component(component_code="code_1", version="2", component_cls=component_cls)
        self.assertEqual(
            ComponentLibrary.components,
            {
                "new_test_component": {
                    LEGACY_PLUGINS_VERSION: ComponentLibrary.get_component_class("new_test_component")
                },
                "code_1": {"1": component_cls, "2": component_cls},
            },
        )

    def test_component_list(self):
        class TestService(Service):
            pass

        class TestComponent(Component):
            name = "name"
            code = "code"
            bound_service = TestService
            form = "form path"

            def clean_execute_data(self, context):
                pass

            def outputs_format(self):
                pass

        class TestComponent2(Component):
            name = "name"
            code = "code_2"
            bound_service = TestService
            form = "form path"
            version = "1.0"

            def clean_execute_data(self, context):
                pass

            def outputs_format(self):
                pass

        expect_list = []
        for _, component_map in ComponentLibrary.components.items():
            expect_list.extend(component_map.values())

        component_list = ComponentLibrary.component_list()

        self.assertEqual(component_list, expect_list)
        self.assertEqual(len(component_list), 3)
