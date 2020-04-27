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
from mock import MagicMock, patch

from auth_backend.resources import base
from auth_backend.resources.base import Action, ActionCollection, Resource
from auth_backend.tests.mock_path import *  # noqa


class TestUseResource(Resource):
    pass


class ResourceTestCase(TestCase):
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

        self.resource = TestUseResource(rtype=self.rtype,
                                        name=self.name,
                                        scope_type=self.scope_type,
                                        scope_name=self.scope_name,
                                        actions=self.actions,
                                        inspect=self.inspect,
                                        scope_id=self.scope_id,
                                        parent=self.parent,
                                        operations=self.operations,
                                        backend=self.backend,
                                        properties=['p1', 'p2'])

    def tearDown(self):
        base.resource_type_lib = {}

    def test_init(self):
        self.assertIsInstance(self.resource.actions, ActionCollection)
        view_op, view_action = 0, 0
        edit_op, edit_action = 1, 1
        self.assertEqual(self.resource.operations[view_op]['actions'], [self.actions[view_action].dict()])
        self.assertEqual(self.resource.operations[edit_op]['actions'], [self.actions[view_action].dict(),
                                                                        self.actions[edit_action].dict()])
        self.assertTrue(self.resource.rtype in base.resource_type_lib)

    @patch(RESOURCE_BASE_CONF_SYSTEM_ID, 'system_id_token')
    @patch(RESOURCE_BASE_CONF_SYSTEM_NAME, 'system_name_token')
    @patch(CONF_SCOPE_TYPE_NAMES, {'scope_type_token': 'system_type_name_token'})
    def test_base_info(self):
        self.assertEqual(
            self.resource.base_info(), {
                'system_id': 'system_id_token',
                'system_name': 'system_name_token',
                'scope_type': self.scope_type,
                'scope_type_name': 'system_type_name_token',
                'scope_id': self.scope_id,
                'scope_name': self.scope_name,
                'resource': {
                    'resource_type': self.rtype,
                    'resource_type_name': self.name
                }
            }
        )

    def test_snapshot(self):
        self.assertEqual(self.resource.snapshot(), {'resource_type': self.rtype,
                                                    'resource_type_name': self.name,
                                                    'parent_resource_type': self.parent.rtype,
                                                    'actions': [{
                                                        'action_id': action.id,
                                                        'action_name': action.name,
                                                        'is_related_resource': action.is_instance_related
                                                    } for action in self.actions],
                                                    'properties': ['p1', 'p2']})

    def test_snapshot__properties_is_empty(self):
        self.resource.properties = None
        self.assertEqual(self.resource.snapshot(), {'resource_type': self.rtype,
                                                    'resource_type_name': self.name,
                                                    'parent_resource_type': self.parent.rtype,
                                                    'actions': [{
                                                        'action_id': action.id,
                                                        'action_name': action.name,
                                                        'is_related_resource': action.is_instance_related
                                                    } for action in self.actions]})

    def test_snapshot__parent_is_none(self):
        self.resource.parent = None
        self.assertEqual(self.resource.snapshot()['parent_resource_type'], '')

    def test_real_scope_id(self):
        self.assertEqual(self.resource.real_scope_id(None, None), self.resource.scope_id)

    def test_real_scope_id__inspect_from_instance(self):
        inspect_scope_id = 'inspect_scope_id'
        self.resource.inspect.scope_id = MagicMock(return_value=inspect_scope_id)
        self.resource.scope_id = None

        instance = 'instance'

        self.assertEqual(self.resource.real_scope_id(instance, None), inspect_scope_id)
        self.resource.inspect.scope_id.assert_called_once_with(instance)

    def test_real_scope_id__use_candidate(self):
        self.resource.scope_id = None

        candidate = 'candidate'
        self.assertEqual(self.resource.real_scope_id(None, candidate), candidate)
        self.resource.inspect.scope_id.assert_not_called()

    def test_clean_instances(self):
        clean_str_instance_return = 'clean_str_instance_return'
        clean_list_instance_return = 'clean_list_instance_return'
        self.resource.clean_str_instances = MagicMock(return_value=clean_str_instance_return)
        self.resource.clean_unicode_instances = MagicMock(return_value=clean_str_instance_return)
        self.resource.clean_list_instances = MagicMock(return_value=clean_list_instance_return)

        str_instances = 'str_instances'
        list_instances = ['instance']

        self.assertEqual(self.resource.clean_instances(str_instances), clean_str_instance_return)
        self.assertEqual(self.resource.clean_instances(list_instances), clean_list_instance_return)
        self.resource.clean_list_instances.assert_called_once_with(list_instances)

    def test_clean_instances__instances_is_none(self):
        self.assertIsNone(self.resource.clean_instances(None))

    @patch(RESOURCE_CLEAN_INSTANCE, MagicMock(return_value='clean_instance_token'))
    def test_resource_id(self):
        instance = 'instance'
        self.assertIsNotNone(self.resource.resource_id(instance))
        self.resource.clean_instances.assert_called_once_with(instance)
        self.resource.inspect.resource_id.assert_called_once_with('clean_instance_token')

    @patch(RESOURCE_CLEAN_INSTANCE, MagicMock(return_value='clean_instance_token'))
    def test_resource_name(self):
        instance = 'instance'
        self.assertIsNotNone(self.resource.resource_name(instance))
        self.resource.clean_instances.assert_called_once_with(instance)
        self.resource.inspect.resource_name.assert_called_once_with('clean_instance_token')

    @patch(RESOURCE_CLEAN_INSTANCE, MagicMock(return_value='clean_instance_token'))
    def test_creator_type(self):
        instance = 'instance'
        self.assertIsNotNone(self.resource.creator_type(instance))
        self.resource.clean_instances.assert_called_once_with(instance)
        self.resource.inspect.creator_type.assert_called_once_with('clean_instance_token')

    @patch(RESOURCE_CLEAN_INSTANCE, MagicMock(return_value='clean_instance_token'))
    def test_creator_id(self):
        instance = 'instance'
        self.assertIsNotNone(self.resource.creator_id(instance))
        self.resource.clean_instances.assert_called_once_with(instance)
        self.resource.inspect.creator_id.assert_called_once_with('clean_instance_token')

    @patch(RESOURCE_CLEAN_INSTANCE, MagicMock(return_value='clean_instance_token'))
    def test_parent_instance(self):
        child = 'child'
        self.assertIsNotNone(self.resource.parent_instance(child))
        self.resource.inspect.parent.assert_called_once_with('child')

    @patch(RESOURCE_CLEAN_INSTANCE, MagicMock(return_value='clean_instance_token'))
    def test_properties(self):
        instance = 'instance'
        self.assertIsNotNone(self.resource.resource_properties(instance))
        self.resource.inspect.properties.assert_called_once_with('instance')

    def test_is_instance_related_action(self):
        view_action = 0
        action = self.actions[view_action]
        self.assertEqual(action.is_instance_related, self.resource.is_instance_related_action(action.id))

    @patch(RESOURCE_CLEAN_INSTANCE, MagicMock(return_value='clean_instance_token'))
    @patch(RESOURCE_REAL_SCOPE_ID, MagicMock(return_value='real_scope_id_token'))
    def test_register_instance(self):
        instance = 'instance'
        scope_id = 'scope_id'
        self.assertIsNotNone(self.resource.register_instance(instance, scope_id))
        self.resource.clean_instances.assert_called_once_with(instance)
        self.resource.real_scope_id.assert_called_once_with('clean_instance_token', scope_id)
        self.resource.backend.register_instance.assert_called_once_with(resource=self.resource,
                                                                        instance='clean_instance_token',
                                                                        scope_id='real_scope_id_token')

    @patch(RESOURCE_CLEAN_INSTANCE, MagicMock(return_value=['clean_instance_token']))
    @patch(RESOURCE_REAL_SCOPE_ID, MagicMock(return_value='real_scope_id_token'))
    def test_batch_register_instance(self):
        instances = ['instances']
        scope_id = 'scope_id'
        self.assertIsNotNone(self.resource.batch_register_instance(instances, scope_id))
        self.resource.clean_instances.assert_called_once_with(instances)
        self.resource.real_scope_id.assert_called_once_with('clean_instance_token', scope_id)
        self.resource.backend.batch_register_instance.assert_called_once_with(resource=self.resource,
                                                                              instances=['clean_instance_token'],
                                                                              scope_id='real_scope_id_token')

    @patch(RESOURCE_CLEAN_INSTANCE, MagicMock(return_value='clean_instance_token'))
    @patch(RESOURCE_REAL_SCOPE_ID, MagicMock(return_value='real_scope_id_token'))
    def test_update_instance(self):
        instance = 'instance'
        scope_id = 'scope_id'
        self.assertIsNotNone(self.resource.update_instance(instance, scope_id))
        self.resource.clean_instances.assert_called_once_with(instance)
        self.resource.real_scope_id.assert_called_once_with('clean_instance_token', scope_id)
        self.resource.backend.update_instance.assert_called_once_with(resource=self.resource,
                                                                      instance='clean_instance_token',
                                                                      scope_id='real_scope_id_token')

    @patch(RESOURCE_CLEAN_INSTANCE, MagicMock(return_value='clean_instance_token'))
    @patch(RESOURCE_REAL_SCOPE_ID, MagicMock(return_value='real_scope_id_token'))
    def test_delete_instance(self):
        instance = 'instance'
        scope_id = 'scope_id'
        self.assertIsNotNone(self.resource.delete_instance(instance, scope_id))
        self.resource.clean_instances.assert_called_once_with(instance)
        self.resource.real_scope_id.assert_called_once_with('clean_instance_token', scope_id)
        self.resource.backend.delete_instance.assert_called_once_with(resource=self.resource,
                                                                      instance='clean_instance_token',
                                                                      scope_id='real_scope_id_token')

    @patch(RESOURCE_CLEAN_INSTANCE, MagicMock(return_value=['clean_instance_token']))
    @patch(RESOURCE_REAL_SCOPE_ID, MagicMock(return_value='real_scope_id_token'))
    def test_batch_delete_instance(self):
        instances = ['instances']
        scope_id = 'scope_id'
        self.assertIsNotNone(self.resource.batch_delete_instance(instances, scope_id))
        self.resource.clean_instances.assert_called_once_with(instances)
        self.resource.real_scope_id.assert_called_once_with('clean_instance_token', scope_id)
        self.resource.backend.batch_delete_instance.assert_called_once_with(resource=self.resource,
                                                                            instances=['clean_instance_token'],
                                                                            scope_id='real_scope_id_token')

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
