# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from __future__ import absolute_import, unicode_literals

from django.test import TestCase
from mock import MagicMock

from auth_backend.resources.inspect import FieldInspect


class FieldInspectTestCase(TestCase):
    def setUp(self):
        self.instance = MagicMock()
        self.instance.creator_type = 'creator_type_token'
        self.instance.creator_id = 'creator_id_token'
        self.instance.resource_id = 'resource_id_token'
        self.instance.resource_name = 'resource_name_token'
        self.instance.parent = 'parent_token'
        self.instance.scope_id = 'scope_id_token'

        self.inspect = FieldInspect(creator_type_f='creator_type',
                                    creator_id_f='creator_id',
                                    resource_id_f='resource_id',
                                    resource_name_f='resource_name',
                                    parent_f='parent',
                                    scope_id_f='scope_id',
                                    properties_map={
                                        'creator_id': 'creator',
                                        'scope_id': 'scope_id'
                                    }
                                    )

    def test_field_inspect(self):
        fields = [
            'creator_type',
            'creator_id',
            'resource_id',
            'resource_name',
            'parent',
            'scope_id'
        ]
        for f in fields:
            self.assertEqual(getattr(self.instance, f), getattr(self.inspect, f)(self.instance))

    def test_properties(self):
        properties = self.inspect.properties(self.instance)
        self.assertEqual(
            properties,
            {
                'creator': 'creator_id_token',
                'scope_id': 'scope_id_token'
            }
        )

    def test__get_none_field(self):
        self.inspect.creator_type_f = None
        self.assertIsNone(self.inspect.creator_type(self.instance))
