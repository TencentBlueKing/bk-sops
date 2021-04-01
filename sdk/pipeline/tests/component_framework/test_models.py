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

__group_name__ = "gn"
__group_icon__ = "gi"


class TestModels(TestCase):
    @classmethod
    def setUpClass(cls):
        ComponentModel.objects.all().delete()  # env clean

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        class CCUpdateHostModuleService(Service):
            def execute(self, data, parent_data):
                pass

            def outputs(self):
                return [
                    self.OutputItem(name="key_1", key="key_1", type="int"),
                    self.OutputItem(name="key_2", key="key_2", type="str"),
                ]

            def outputs_format(self):
                pass

        class CCUpdateHostModuleComponent(Component):
            name = "1234"
            bound_service = CCUpdateHostModuleService
            code = "cc_update_module"
            form = "form path"

        class CCUpdateHostModuleComponentV2(Component):
            name = "1234"
            bound_service = CCUpdateHostModuleService
            code = "cc_update_module"
            form = "form path"
            version = "2.0"

        self.service = CCUpdateHostModuleService
        self.component = CCUpdateHostModuleComponent
        self.component_v2 = CCUpdateHostModuleComponentV2

    def tearDown(self):
        ComponentModel.objects.all().delete()
        ComponentLibrary.components = {}

    def test_unicode(self):
        component = ComponentModel.objects.get(code=self.component.code, version=LEGACY_PLUGINS_VERSION)
        self.assertEqual(component.name, component.__unicode__())

    def test_group_name(self):
        component = ComponentModel.objects.get(code=self.component.code, version=LEGACY_PLUGINS_VERSION)
        self.assertEqual(component.group_name, self.component.group_name)

    def test_version(self):
        component = ComponentModel.objects.get(code=self.component.code, version=LEGACY_PLUGINS_VERSION)
        component_v2 = ComponentModel.objects.get(code=self.component.code, version="2.0")
        self.assertEqual(component.version, LEGACY_PLUGINS_VERSION)
        self.assertEqual(component_v2.version, "2.0")

    def test_group_icon(self):
        component = ComponentModel.objects.get(code=self.component.code, version=LEGACY_PLUGINS_VERSION)
        self.assertEqual(component.group_icon, self.component.group_icon)

    def test_get_component_dict(self):
        d = ComponentModel.objects.get_component_dict()
        self.assertEqual(d, {"cc_update_module": "gn-1234"})
