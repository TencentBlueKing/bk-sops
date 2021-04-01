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
from pipeline.component_framework.library import ComponentLibrary
from pipeline.component_framework.models import ComponentModel
from pipeline.core.flow.activity import Service


class TestBase(TestCase):
    def tearDown(self):
        ComponentModel.objects.all().delete()
        ComponentLibrary.components = {}

    def test_no_name_component(self):
        class NoNameComponentService(Service):
            def execute(self, data, parent_data):
                pass

        try:

            class NoNameComponent(Component):
                bound_service = NoNameComponentService
                code = "no_name_component"
                form = "form_path"

                def outputs_format(cls):
                    return {}

                def clean_execute_data(self, context):
                    return {}

        except ValueError as e:
            self.assertNotEqual(str(e).find("name"), -1)

    def test_no_code_component(self):
        class NoCodeComponentService(Service):
            def execute(self, data, parent_data):
                pass

        try:

            class NoCodeComponent(Component):
                bound_service = NoCodeComponentService
                name = "no code component"
                form = "form_path"

                def outputs_format(cls):
                    return {}

                def clean_execute_data(self, context):
                    return {}

        except ValueError as e:
            self.assertNotEqual(str(e).find("code"), -1)

    def test_no_form_component(self):
        class NoFormComponentService(Service):
            def execute(self, data, parent_data):
                pass

        try:

            class NoCodeComponent(Component):
                bound_service = NoFormComponentService
                name = "no form component"
                code = "no_form_component"

                def outputs_format(cls):
                    return {}

                def clean_execute_data(self, context):
                    return {}

        except ValueError as e:
            self.assertNotEqual(str(e).find("form"), -1)

    def test_no_service_component(self):
        try:

            class NoServiceComponent(Component):
                name = "no service component"
                code = "no_service_component"
                form = "form_path"

                def outputs_format(cls):
                    return {}

                def clean_execute_data(self, context):
                    return {}

        except ValueError as e:
            self.assertNotEqual(str(e).find("service"), -1)

    def test_wrong_class_service_component(self):
        try:

            class WrongClassComponent(Component):
                name = "wrong class component"
                code = "wrong_class_component"
                form = "form_path"
                bound_service = int

            def outputs_format(cls):
                return {}

            def clean_execute_data(self, context):
                return {}

        except ValueError as e:
            self.assertNotEqual(str(e).find("service"), -1)
