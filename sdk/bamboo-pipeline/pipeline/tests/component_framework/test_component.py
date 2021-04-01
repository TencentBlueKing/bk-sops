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
from pipeline.core.data.base import DataObject
from pipeline.core.data.var import PlainVariable
from pipeline.core.flow.activity import Service
from pipeline.exceptions import ComponentDataLackException


class TestComponent(TestCase):
    def setUp(self):
        class CCUpdateHostModuleService(Service):
            def execute(self, data, parent_data):
                pass

            def outputs(self):
                return [
                    self.OutputItem(name="key_1", key="key_1", type="int"),
                    self.OutputItem(name="key_2", key="key_2", type="str"),
                ]

            def inputs(self):
                return [
                    self.InputItem(name="key_3", key="key_3", type="int", required=True),
                    self.InputItem(name="key_4", key="key_4", type="int", required=False),
                ]

        class CCUpdateHostModuleComponent(Component):
            name = "修改主机所属模块"
            bound_service = CCUpdateHostModuleService
            code = "cc_update_module"
            form = "form path"

        class CCUpdateHostModuleComponentEmbeddedForm(Component):
            name = "修改主机所属模块"
            bound_service = CCUpdateHostModuleService
            code = "cc_update_module_embedded_form"
            embedded_form = True
            form = "form path"

        self.service = CCUpdateHostModuleService
        self.component = CCUpdateHostModuleComponent
        self.component_embedded_form = CCUpdateHostModuleComponentEmbeddedForm

    def tearDown(self):
        ComponentModel.objects.all().delete()
        ComponentLibrary.components = {}

    def test_init(self):
        self.component({})

    def test_outputs_format(self):
        outputs_format = self.component({}).outputs_format()
        self.assertEqual(
            outputs_format,
            [
                {"name": "key_1", "key": "key_1", "type": "int", "schema": {}},
                {"name": "key_2", "key": "key_2", "type": "str", "schema": {}},
            ],
        )

    def test_inputs_format(self):
        inputs_format = self.component({}).inputs_format()
        self.assertEqual(
            inputs_format,
            [
                {"name": "key_3", "key": "key_3", "type": "int", "required": True, "schema": {}},
                {"name": "key_4", "key": "key_4", "type": "int", "required": False, "schema": {}},
            ],
        )

    def test_clean_execution_data(self):
        data = {"test": "test"}
        data_after_clean = self.component(data).clean_execute_data(None)
        self.assertEqual(data, data_after_clean)

    def test_service(self):
        service = self.component({}).service()
        self.assertIsInstance(service, self.service)

    def test_data_for_execution(self):
        v1 = PlainVariable(name="key_1", value="value_1")
        v2 = PlainVariable(name="key_2", value="value_2")
        data = {"key_1": {"value": v1}, "key_2": {"value": v2}}
        component = self.component(data)
        execution_data = component.data_for_execution({}, {})
        self.assertIsInstance(execution_data, DataObject)
        self.assertEqual(execution_data.get_inputs(), {"key_1": v1, "key_2": v2})

    def test_data_for_execution_lack_of_inputs(self):
        PlainVariable(name="key_1", value="value_1")
        data = {"key_1": None, "key_2": None}
        component = self.component(data)
        self.assertRaises(ComponentDataLackException, execution_data=component.data_for_execution, args=[None, None])

    def test_form_is_embedded(self):
        self.assertFalse(self.component.form_is_embedded())
        self.assertTrue(self.component_embedded_form.form_is_embedded())
