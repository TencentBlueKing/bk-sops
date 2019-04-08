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
from pipeline.component_framework.models import ComponentModel
from pipeline.component_framework.library import ComponentLibrary

__register_ignore__ = True


class TestBaseIgnoreComponent(TestCase):

    def tearDown(self):
        ComponentModel.objects.all().delete()
        ComponentLibrary.components = {}

    def test_ignore_component(self):
        class IgnoreService(Service):
            def execute(self, data, parent_data):
                pass

        class IgnoreComponent(Component):
            name = u'ignore_service'
            bound_service = IgnoreService
            code = 'ignore_component'
            form = 'form path'

            def outputs_format(self):
                return {
                    'result': bool,
                    'message': str
                }

            def clean_execute_data(self, context):
                return {}

        self.assertIsNone(ComponentLibrary.get_component_class('ignore_component'))
