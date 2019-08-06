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

from mock import MagicMock, patch
from django.test import TestCase

from auth_backend.resources import base
from auth_backend.resources.base import ObjectResource, Action

from auth_backend.tests.mock_path import *  # noqa


class ObjectResourceTestCase(TestCase):
    def setUp(self):
        self.rtype = 'type_token'
        self.name = 'name_token'
        self.scope_type = 'scope_type_token'
        self.scope_name = 'scope_name_token'
        self.actions = [Action(id='view', name='view', is_instance_related=True),
                        Action(id='edit', name='edit', is_instance_related=True)]
        self.inspect = MagicMock()
        self.scope_id = 'scope_id_token'
        self.parent = MagicMock()
        self.parent.rtype = 'parent_type_token'
        self.operations = [{
            'operate_id': 'view',
            'actions_id': ['view'],
        }, {
            'operate_id': 'edit',
            'actions_id': ['view', 'edit']
        }]
        self.backend = MagicMock()

    def tearDown(self):
        base.resource_type_lib = {}

    @patch(RESOURCE_CLEAN_INSTANCE, MagicMock())
    def test_clean_instances__is_resource_cls(self):
        resource = ObjectResource(rtype=self.rtype,
                                  name=self.name,
                                  scope_type=self.scope_type,
                                  scope_name=self.scope_name,
                                  actions=self.actions,
                                  inspect=self.inspect,
                                  scope_id=self.scope_id,
                                  parent=self.parent,
                                  operations=self.operations,
                                  backend=self.backend,
                                  resource_cls=str)

        instance = 'instance'
        self.assertEqual(resource.clean_instances(instance), instance)
        super(ObjectResource, resource).clean_instances.assert_not_called()

    @patch(RESOURCE_CLEAN_INSTANCE, MagicMock())
    def test_clean_instances__fall_back_to_super(self):
        resource = ObjectResource(rtype=self.rtype,
                                  name=self.name,
                                  scope_type=self.scope_type,
                                  scope_name=self.scope_name,
                                  actions=self.actions,
                                  inspect=self.inspect,
                                  scope_id=self.scope_id,
                                  parent=self.parent,
                                  operations=self.operations,
                                  backend=self.backend,
                                  resource_cls=list)

        instance = 'instance'
        self.assertIsNotNone(resource.clean_instances(instance))
        super(ObjectResource, resource).clean_instances.assert_called_once_with(instance)
