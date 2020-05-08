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

from mock import MagicMock, patch
from django.test import TestCase

from auth_backend.resources import base
from auth_backend.resources.base import Action, NeverInitiateResource
from auth_backend.resources.inspect import DummyInspect

from auth_backend.tests.mock_path import *  # noqa


class NeverInitiateResourceTestCase(TestCase):
    def setUp(self):
        self.rtype = 'type_token'
        self.name = 'name_token'
        self.scope_type = 'scope_type_token'
        self.scope_name = 'scope_name_token'
        self.actions = [Action(id='view', name='view', is_instance_related=False),
                        Action(id='edit', name='edit', is_instance_related=False)]
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

        self.resource = NeverInitiateResource(rtype=self.rtype,
                                              name=self.name,
                                              scope_type=self.scope_type,
                                              scope_name=self.scope_name,
                                              actions=self.actions,
                                              scope_id=self.scope_id,
                                              operations=self.operations,
                                              backend=self.backend)

    def tearDown(self):
        base.resource_type_lib = {}

    def test_init(self):
        self.assertIsInstance(self.resource.inspect, DummyInspect)

    @patch(RESOURCE_CLEAN_INSTANCE, MagicMock(return_value='clean_instance_token'))
    @patch(RESOURCE_REAL_SCOPE_ID, MagicMock(return_value='real_scope_id_token'))
    def test_verify_perms(self):
        principal_type = 'principal_type_token'
        principal_id = 'principal_id_token'
        action_ids = 'action_ids'
        instance = 'instance'
        scope_id = 'scope_id'
        self.assertIsNotNone(self.resource.verify_perms(principal_type, principal_id, action_ids, instance, scope_id))
        self.resource.clean_instances.assert_called_once_with(instance)
        self.resource.real_scope_id.assert_called_once_with('clean_instance_token', scope_id)
        self.resource.backend.verify_perms.assert_called_once_with(principal_type=principal_type,
                                                                   principal_id=principal_id,
                                                                   resource=self.resource,
                                                                   instance='clean_instance_token',
                                                                   action_ids=action_ids,
                                                                   scope_id='real_scope_id_token')

    @patch(RESOURCE_CLEAN_INSTANCE, MagicMock(return_value=['clean_instance_token']))
    @patch(RESOURCE_REAL_SCOPE_ID, MagicMock(return_value='real_scope_id_token'))
    def test_batch_verify_perms(self):
        principal_type = 'principal_type_token'
        principal_id = 'principal_id_token'
        action_ids = 'action_ids'
        instances = ['instance']
        scope_id = 'scope_id'
        self.assertIsNotNone(self.resource.batch_verify_perms(principal_type, principal_id, action_ids, instances,
                                                              scope_id))
        self.resource.clean_instances.assert_called_once_with(instances)
        self.resource.real_scope_id.assert_called_once_with('clean_instance_token', scope_id)
        self.resource.backend.batch_verify_perms.assert_called_once_with(principal_type=principal_type,
                                                                         principal_id=principal_id,
                                                                         resource=self.resource,
                                                                         instances=['clean_instance_token'],
                                                                         action_ids=action_ids,
                                                                         scope_id='real_scope_id_token')

    @patch(RESOURCE_REAL_SCOPE_ID, MagicMock(return_value='real_scope_id_token'))
    def test_search_resources_perms_principals(self):
        resources_actions = 'resource_actions_token'
        scope_id = 'scope_id'
        self.assertIsNotNone(self.resource.search_resources_perms_principals(resources_actions, scope_id))
        self.resource.real_scope_id.assert_called_once_with(None, scope_id)
