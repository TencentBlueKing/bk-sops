# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
from django.test import TestCase

from pipeline.core.flow.activity import Service
from pipeline.component_framework.component import Component
from pipeline.component_framework.library import ComponentLibrary


class TestRegistry(TestCase):
    def test_component(self):
        class TestService(Service):
            pass

        class TestComponent(Component):
            name = 'name'
            code = 'code'
            bound_service = TestService

        self.assertEqual(ComponentLibrary.components['code'], TestComponent)

    def test_get_component(self):
        class TestService(Service):
            pass

        class TestComponent(Component):
            name = 'name'
            code = 'code'
            bound_service = TestService

            def clean_execute_data(self, context):
                pass

            def outputs_format(self):
                pass

        self.assertEqual(ComponentLibrary.get_component('code', {}).__class__, TestComponent)
