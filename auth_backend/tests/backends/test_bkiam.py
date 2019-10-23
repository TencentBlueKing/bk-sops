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

from __future__ import absolute_import, unicode_literals

from django.test import TestCase
from mock import MagicMock, call, patch
from six.moves import range

from auth_backend.backends.bkiam import BKIAMBackend
from auth_backend.tests.mock_path import *  # noqa


class BKIAMBackendTestCase(TestCase):
    resource_id = 'resource_id_token'

    def setUp(self):
        self.backend = BKIAMBackend(client=MagicMock())
        self.scope_id = 'scope_id_token'
        self.real_scope_id = 'real_scope_id_token'
        self.creator_type = 'creator_type_token'
        self.creator_id = 'creator_id_token'
        self.scope_type = 'scope_type_token'
        self.resource_name = 'resource_name_token'
        self.resource_type = 'resource_type_token'
        self.principal_type = 'principal_type_token'
        self.principal_id = 'principal_id_token'
        self.action_ids = ['new', 'view', 'edit']
        self.properties = {'k': 'v', 'k2': 'v2'}

        resource = MagicMock()
        resource.rtype = self.resource_type
        resource.scope_type = self.scope_type
        resource.creator_type = MagicMock(return_value=self.creator_type)
        resource.creator_id = MagicMock(return_value=self.creator_id)
        resource.resource_name = MagicMock(return_value=self.resource_name)
        resource.real_scope_id = MagicMock(return_value=self.real_scope_id)
        resource.resource_properties = MagicMock(return_value=self.properties)

        resource_1 = MagicMock()
        resource_1.rtype = self.resource_type + '_1'
        resource_1.scope_type = self.scope_type + '_1'
        resource_1.creator_type = MagicMock(return_value=self.creator_type + '_1')
        resource_1.creator_id = MagicMock(return_value=self.creator_id + '_1')
        resource_1.resource_name = MagicMock(return_value=self.resource_name + '_1')
        resource_1.real_scope_id = MagicMock(return_value=self.real_scope_id + '_1')

        def is_instance_related_action(action_id):
            return {
                'new': False,
                'view': True,
                'edit': True
            }[action_id]

        resource.is_instance_related_action = is_instance_related_action
        resource_1.is_instance_related_action = is_instance_related_action
        self.resource = resource
        self.resource_1 = resource_1

        self.instance = MagicMock()
        self.instance_1 = MagicMock()

        self.instances = [MagicMock() for _ in range(3)]

    @patch(BACKEND_BKIAM_RESOURCE_ID_FOR, MagicMock(return_value=resource_id))
    @patch(BACKEND_UTILS_RESOURCE_ID_FOR, MagicMock(return_value=resource_id))
    def test_register_instance__with_scope_id(self):
        self.backend.register_instance(resource=self.resource, instance=self.instance, scope_id=self.scope_id)

        self.resource.creator_type.assert_called_once_with(self.instance)
        self.resource.creator_id.assert_called_once_with(self.instance)
        self.resource.real_scope_id.assert_not_called()
        self.resource.resource_name.assert_called_once_with(self.instance)
        self.resource.resource_properties.assert_called_once_with(self.instance)
        self.backend.client.register_resource.assert_called_once_with(
            creator_type=self.creator_type,
            creator_id=self.creator_id,
            scope_type=self.scope_type,
            scope_id=self.scope_id,
            resource_type=self.resource_type,
            resource_name=self.resource_name,
            resource_id=self.resource_id,
            properties=self.properties
        )

    @patch(BACKEND_BKIAM_RESOURCE_ID_FOR, MagicMock(return_value=resource_id))
    @patch(BACKEND_UTILS_RESOURCE_ID_FOR, MagicMock(return_value=resource_id))
    def test_register_instance__without_scope_id(self):
        self.backend.register_instance(resource=self.resource, instance=self.instance)

        self.resource.creator_type.assert_called_once_with(self.instance)
        self.resource.creator_id.assert_called_once_with(self.instance)
        self.resource.real_scope_id.assert_called_once_with(self.instance, None)
        self.resource.resource_name.assert_called_once_with(self.instance)
        self.resource.resource_properties.assert_called_once_with(self.instance)
        self.backend.client.register_resource.assert_called_once_with(
            creator_type=self.creator_type,
            creator_id=self.creator_id,
            scope_type=self.scope_type,
            scope_id=self.real_scope_id,
            resource_type=self.resource_type,
            resource_name=self.resource_name,
            resource_id=self.resource_id,
            properties=self.properties
        )

    @patch(BACKEND_BKIAM_RESOURCE_ID_FOR, MagicMock(return_value=resource_id))
    @patch(BACKEND_UTILS_RESOURCE_ID_FOR, MagicMock(return_value=resource_id))
    def test_register_instance__without_properties(self):
        self.resource.resource_properties = MagicMock(return_value=None)
        self.backend.register_instance(resource=self.resource, instance=self.instance)

        self.resource.creator_type.assert_called_once_with(self.instance)
        self.resource.creator_id.assert_called_once_with(self.instance)
        self.resource.resource_name.assert_called_once_with(self.instance)
        self.resource.resource_properties.assert_called_once_with(self.instance)
        self.resource.resource_properties.assert_called_once_with(self.instance)
        self.backend.client.register_resource.assert_called_once_with(
            creator_type=self.creator_type,
            creator_id=self.creator_id,
            scope_type=self.scope_type,
            scope_id=self.real_scope_id,
            resource_type=self.resource_type,
            resource_name=self.resource_name,
            resource_id=self.resource_id,
            properties={}
        )

    def test_batch_register_instance__with_empty_instances(self):
        self.assertRaises(ValueError, self.backend.batch_register_instance, self.resource, None)
        self.assertRaises(ValueError, self.backend.batch_register_instance, self.resource, [])

    @patch(BACKEND_BKIAM_RESOURCE_ID_FOR, MagicMock(return_value=resource_id))
    @patch(BACKEND_UTILS_RESOURCE_ID_FOR, MagicMock(return_value=resource_id))
    def test_batch_register_instance__with_scope_id(self):
        self.backend.batch_register_instance(resource=self.resource, instances=self.instances, scope_id=self.scope_id)

        self.resource.real_scope_id.assert_not_called()
        self.resource.resource_name.assert_has_calls([call(instance) for instance in self.instances])
        self.resource.resource_properties.assert_has_calls([call(instance) for instance in self.instances])
        self.resource.creator_type.assert_called_once_with(self.instances[0])
        self.resource.creator_id.assert_called_once_with(self.instances[0])
        self.backend.client.batch_register_resource.assert_called_once_with(creator_type=self.creator_type,
                                                                            creator_id=self.creator_id,
                                                                            resources=[{
                                                                                'scope_type': self.scope_type,
                                                                                'scope_id': self.scope_id,
                                                                                'resource_type': self.resource.rtype,
                                                                                'resource_id': self.resource_id,
                                                                                'resource_name': self.resource_name,
                                                                                'properties': self.properties
                                                                            } for _ in self.instances])

    @patch(BACKEND_BKIAM_RESOURCE_ID_FOR, MagicMock(return_value=resource_id))
    @patch(BACKEND_UTILS_RESOURCE_ID_FOR, MagicMock(return_value=resource_id))
    def test_batch_register_instance__without_scope_id(self):
        self.backend.batch_register_instance(resource=self.resource, instances=self.instances)

        self.resource.real_scope_id.assert_has_calls([call(instance, None) for instance in self.instances])
        self.resource.resource_name.assert_has_calls([call(instance) for instance in self.instances])
        self.resource.resource_properties.assert_has_calls([call(instance) for instance in self.instances])
        self.resource.creator_type.assert_called_once_with(self.instances[0])
        self.resource.creator_id.assert_called_once_with(self.instances[0])
        self.backend.client.batch_register_resource.assert_called_once_with(creator_type=self.creator_type,
                                                                            creator_id=self.creator_id,
                                                                            resources=[{
                                                                                'scope_type': self.scope_type,
                                                                                'scope_id': self.real_scope_id,
                                                                                'resource_type': self.resource.rtype,
                                                                                'resource_id': self.resource_id,
                                                                                'resource_name': self.resource_name,
                                                                                'properties': self.properties
                                                                            } for _ in self.instances])

    @patch(BACKEND_BKIAM_RESOURCE_ID_FOR, MagicMock(return_value=resource_id))
    @patch(BACKEND_UTILS_RESOURCE_ID_FOR, MagicMock(return_value=resource_id))
    def test_update_instance__with_scope_id(self):
        self.backend.update_instance(resource=self.resource, instance=self.instance, scope_id=self.scope_id)

        self.resource.real_scope_id.assert_not_called()
        self.resource.resource_name.assert_called_once_with(self.instance)
        self.backend.client.update_resource.assert_called_once_with(scope_type=self.scope_type,
                                                                    scope_id=self.scope_id,
                                                                    resource_type=self.resource_type,
                                                                    resource_id=self.resource_id,
                                                                    resource_name=self.resource_name,
                                                                    properties=self.properties)

    @patch(BACKEND_BKIAM_RESOURCE_ID_FOR, MagicMock(return_value=resource_id))
    @patch(BACKEND_UTILS_RESOURCE_ID_FOR, MagicMock(return_value=resource_id))
    def test_update_instance__without_scope_id(self):
        self.backend.update_instance(resource=self.resource, instance=self.instance)

        self.resource.real_scope_id.assert_called_once_with(self.instance, None)
        self.resource.resource_name.assert_called_once_with(self.instance)
        self.backend.client.update_resource.assert_called_once_with(scope_type=self.scope_type,
                                                                    scope_id=self.real_scope_id,
                                                                    resource_type=self.resource_type,
                                                                    resource_id=self.resource_id,
                                                                    resource_name=self.resource_name,
                                                                    properties=self.properties)

    @patch(BACKEND_BKIAM_RESOURCE_ID_FOR, MagicMock(return_value=resource_id))
    @patch(BACKEND_UTILS_RESOURCE_ID_FOR, MagicMock(return_value=resource_id))
    def test_update_instance__without_properties(self):
        self.resource.resource_properties = MagicMock(return_value=None)
        self.backend.update_instance(resource=self.resource, instance=self.instance, scope_id=self.scope_id)

        self.resource.real_scope_id.assert_not_called()
        self.resource.resource_name.assert_called_once_with(self.instance)
        self.backend.client.update_resource.assert_called_once_with(scope_type=self.scope_type,
                                                                    scope_id=self.scope_id,
                                                                    resource_type=self.resource_type,
                                                                    resource_id=self.resource_id,
                                                                    resource_name=self.resource_name,
                                                                    properties={})

    @patch(BACKEND_BKIAM_RESOURCE_ID_FOR, MagicMock(return_value=resource_id))
    @patch(BACKEND_UTILS_RESOURCE_ID_FOR, MagicMock(return_value=resource_id))
    def test_delete_instance__with_scope_id(self):
        self.backend.delete_instance(resource=self.resource, instance=self.instance, scope_id=self.scope_id)

        self.resource.real_scope_id.assert_not_called()
        self.backend.client.delete_resource.assert_called_once_with(scope_type=self.scope_type,
                                                                    scope_id=self.scope_id,
                                                                    resource_type=self.resource_type,
                                                                    resource_id=self.resource_id)

    @patch(BACKEND_BKIAM_RESOURCE_ID_FOR, MagicMock(return_value=resource_id))
    @patch(BACKEND_UTILS_RESOURCE_ID_FOR, MagicMock(return_value=resource_id))
    def test_delete_instance__without_scope_id(self):
        self.backend.delete_instance(resource=self.resource, instance=self.instance)

        self.resource.real_scope_id.assert_called_once_with(self.instance, None)
        self.backend.client.delete_resource.assert_called_once_with(scope_type=self.scope_type,
                                                                    scope_id=self.real_scope_id,
                                                                    resource_type=self.resource_type,
                                                                    resource_id=self.resource_id)

    def test_batch_delete__with_empty_instances(self):
        self.assertRaises(ValueError, self.backend.batch_delete_instance, self.resource, None)
        self.assertRaises(ValueError, self.backend.batch_delete_instance, self.resource, [])

    @patch(BACKEND_BKIAM_RESOURCE_ID_FOR, MagicMock(return_value=resource_id))
    @patch(BACKEND_UTILS_RESOURCE_ID_FOR, MagicMock(return_value=resource_id))
    def test_batch_delete_instance__with_scope_id(self):
        self.backend.batch_delete_instance(resource=self.resource, instances=self.instances, scope_id=self.scope_id)

        self.resource.real_scope_id.assert_not_called()
        self.resource.resource_name.assert_has_calls([call(instance) for instance in self.instances])
        self.backend.client.batch_delete_resource.assert_called_once_with(resources=[{
            'scope_type': self.scope_type,
            'scope_id': self.scope_id,
            'resource_type': self.resource_type,
            'resource_id': self.resource_id,
            'resource_name': self.resource_name
        } for _ in self.instances])

    @patch(BACKEND_BKIAM_RESOURCE_ID_FOR, MagicMock(return_value=resource_id))
    @patch(BACKEND_UTILS_RESOURCE_ID_FOR, MagicMock(return_value=resource_id))
    def test_batch_delete_instance__without_scope_id(self):
        self.backend.batch_delete_instance(resource=self.resource, instances=self.instances)

        self.resource.real_scope_id.assert_has_calls([call(instance, None) for instance in self.instances])
        self.resource.resource_name.assert_has_calls([call(instance) for instance in self.instances])
        self.backend.client.batch_delete_resource.assert_called_once_with(resources=[{
            'scope_type': self.scope_type,
            'scope_id': self.real_scope_id,
            'resource_type': self.resource_type,
            'resource_id': self.resource_id,
            'resource_name': self.resource_name
        } for _ in self.instances])

    @patch(BACKEND_BKIAM_RESOURCE_ID_FOR, MagicMock(return_value=resource_id))
    @patch(BACKEND_UTILS_RESOURCE_ID_FOR, MagicMock(return_value=resource_id))
    def test_verify_perms__with_scope_id_and_instance(self):
        self.backend.verify_perms(resource=self.resource,
                                  principal_type=self.principal_type,
                                  principal_id=self.principal_id,
                                  action_ids=self.action_ids,
                                  instance=self.instance,
                                  scope_id=self.scope_id)

        resource_actions = [{'action_id': 'new',
                             'resource_type': self.resource_type},
                            {'action_id': 'view',
                             'resource_type': self.resource_type,
                             'resource_id': self.resource_id},
                            {'action_id': 'edit',
                             'resource_type': self.resource_type,
                             'resource_id': self.resource_id}]

        self.resource.real_scope_id.assert_not_called()
        self.backend.client.batch_verify_resources_perms.assert_called_once_with(
            principal_type=self.principal_type,
            principal_id=self.principal_id,
            scope_type=self.scope_type,
            scope_id=self.scope_id,
            resources_actions=resource_actions)

    @patch(BACKEND_BKIAM_RESOURCE_ID_FOR, MagicMock(return_value=resource_id))
    @patch(BACKEND_UTILS_RESOURCE_ID_FOR, MagicMock(return_value=resource_id))
    def test_verify_perms__with_scope_id_and_none_instance(self):
        self.backend.verify_perms(resource=self.resource,
                                  principal_type=self.principal_type,
                                  principal_id=self.principal_id,
                                  action_ids=self.action_ids,
                                  scope_id=self.scope_id)

        resource_actions = [{'action_id': 'new',
                             'resource_type': self.resource_type},
                            {'action_id': 'view',
                             'resource_type': self.resource_type},
                            {'action_id': 'edit',
                             'resource_type': self.resource_type}]

        self.resource.real_scope_id.assert_not_called()
        self.backend.client.batch_verify_resources_perms.assert_called_once_with(
            principal_type=self.principal_type,
            principal_id=self.principal_id,
            scope_type=self.scope_type,
            scope_id=self.scope_id,
            resources_actions=resource_actions)

    @patch(BACKEND_BKIAM_RESOURCE_ID_FOR, MagicMock(return_value=resource_id))
    @patch(BACKEND_UTILS_RESOURCE_ID_FOR, MagicMock(return_value=resource_id))
    def test_verify_perms__without_scope_id(self):
        self.backend.verify_perms(resource=self.resource,
                                  principal_type=self.principal_type,
                                  principal_id=self.principal_id,
                                  action_ids=self.action_ids,
                                  instance=self.instance)

        resource_actions = [{'action_id': 'new',
                             'resource_type': self.resource_type},
                            {'action_id': 'view',
                             'resource_type': self.resource_type,
                             'resource_id': self.resource_id},
                            {'action_id': 'edit',
                             'resource_type': self.resource_type,
                             'resource_id': self.resource_id}]

        self.resource.real_scope_id.assert_called_once_with(self.instance, None)
        self.backend.client.batch_verify_resources_perms.assert_called_once_with(
            principal_type=self.principal_type,
            principal_id=self.principal_id,
            scope_type=self.scope_type,
            scope_id=self.real_scope_id,
            resources_actions=resource_actions)

    @patch(BACKEND_BKIAM_RESOURCE_ID_FOR, MagicMock(return_value=resource_id))
    @patch(BACKEND_UTILS_RESOURCE_ID_FOR, MagicMock(return_value=resource_id))
    def test_batch_verify_perms__with_scope_id_and_instances(self):
        self.instances = [MagicMock() for _ in range(2)]
        self.backend.batch_verify_perms(resource=self.resource,
                                        principal_type=self.principal_type,
                                        principal_id=self.principal_id,
                                        action_ids=self.action_ids,
                                        instances=self.instances,
                                        scope_id=self.scope_id)

        resources_actions = [{'action_id': 'new',
                              'resource_type': self.resource_type},
                             {'action_id': 'view',
                              'resource_type': self.resource_type,
                              'resource_id': self.resource_id},
                             {'action_id': 'view',
                              'resource_type': self.resource_type,
                              'resource_id': self.resource_id},
                             {'action_id': 'edit',
                              'resource_type': self.resource_type,
                              'resource_id': self.resource_id},
                             {'action_id': 'edit',
                              'resource_type': self.resource_type,
                              'resource_id': self.resource_id}]

        self.resource.real_scope_id.assert_not_called()
        self.backend.client.batch_verify_resources_perms.assert_called_once_with(principal_type=self.principal_type,
                                                                                 principal_id=self.principal_id,
                                                                                 scope_type=self.scope_type,
                                                                                 scope_id=self.scope_id,
                                                                                 resources_actions=resources_actions)

    @patch(BACKEND_BKIAM_RESOURCE_ID_FOR, MagicMock(return_value=resource_id))
    @patch(BACKEND_UTILS_RESOURCE_ID_FOR, MagicMock(return_value=resource_id))
    def test_batch_verify_perms__with_scope_id_and_none_instances(self):
        self.backend.batch_verify_perms(resource=self.resource,
                                        principal_type=self.principal_type,
                                        principal_id=self.principal_id,
                                        action_ids=self.action_ids,
                                        scope_id=self.scope_id)

        resources_actions = [{'action_id': 'new',
                              'resource_type': self.resource_type}]

        self.resource.real_scope_id.assert_not_called()
        self.backend.client.batch_verify_resources_perms.assert_called_once_with(principal_type=self.principal_type,
                                                                                 principal_id=self.principal_id,
                                                                                 scope_type=self.scope_type,
                                                                                 scope_id=self.scope_id,
                                                                                 resources_actions=resources_actions)

    @patch(BACKEND_BKIAM_RESOURCE_ID_FOR, MagicMock(return_value=resource_id))
    @patch(BACKEND_UTILS_RESOURCE_ID_FOR, MagicMock(return_value=resource_id))
    def test_batch_verify_perms__without_scope_id_and_instances(self):
        self.instances = [MagicMock() for _ in range(2)]
        self.backend.batch_verify_perms(resource=self.resource,
                                        principal_type=self.principal_type,
                                        principal_id=self.principal_id,
                                        action_ids=self.action_ids,
                                        instances=self.instances)

        resources_actions = [{'action_id': 'new',
                              'resource_type': self.resource_type},
                             {'action_id': 'view',
                              'resource_type': self.resource_type,
                              'resource_id': self.resource_id},
                             {'action_id': 'view',
                              'resource_type': self.resource_type,
                              'resource_id': self.resource_id},
                             {'action_id': 'edit',
                              'resource_type': self.resource_type,
                              'resource_id': self.resource_id},
                             {'action_id': 'edit',
                              'resource_type': self.resource_type,
                              'resource_id': self.resource_id}]

        self.resource.real_scope_id.assert_called_once_with(self.instances[0], None)
        self.backend.client.batch_verify_resources_perms.assert_called_once_with(principal_type=self.principal_type,
                                                                                 principal_id=self.principal_id,
                                                                                 scope_type=self.scope_type,
                                                                                 scope_id=self.real_scope_id,
                                                                                 resources_actions=resources_actions)

    @patch(BACKEND_BKIAM_RESOURCE_ID_FOR, MagicMock(return_value=resource_id))
    @patch(BACKEND_UTILS_RESOURCE_ID_FOR, MagicMock(return_value=resource_id))
    def test_batch_verify_perms__without_scope_id_and_none_instances(self):
        self.backend.batch_verify_perms(resource=self.resource,
                                        principal_type=self.principal_type,
                                        principal_id=self.principal_id,
                                        action_ids=self.action_ids)

        resources_actions = [{'action_id': 'new',
                              'resource_type': self.resource_type}]

        self.resource.real_scope_id.assert_called_once_with(None, None)
        self.backend.client.batch_verify_resources_perms.assert_called_once_with(principal_type=self.principal_type,
                                                                                 principal_id=self.principal_id,
                                                                                 scope_type=self.scope_type,
                                                                                 scope_id=self.real_scope_id,
                                                                                 resources_actions=resources_actions)

    @patch(BACKEND_BKIAM_RESOURCE_ID_FOR, MagicMock(return_value=resource_id))
    @patch(BACKEND_UTILS_RESOURCE_ID_FOR, MagicMock(return_value=resource_id))
    def test_verify_multiple_resource_perms__with_scope_id(self):
        perms_tuples = [(self.resource, ['new', 'view'], self.instance),
                        (self.resource, ['new'], None),
                        (self.resource_1, ['new', 'edit'], self.instance_1),
                        (self.resource_1, ['new'], self.instance_1)]

        self.backend.verify_multiple_resource_perms(principal_type=self.principal_type,
                                                    principal_id=self.principal_id,
                                                    perms_tuples=perms_tuples,
                                                    scope_id=self.scope_id)

        resources_actions = [{'action_id': 'new',
                              'resource_type': self.resource_type},
                             {'action_id': 'view',
                              'resource_type': self.resource_type,
                              'resource_id': self.resource_id},
                             {'action_id': 'new',
                              'resource_type': self.resource_type},
                             {'action_id': 'new',
                              'resource_type': self.resource_type + '_1'},
                             {'action_id': 'edit',
                              'resource_type': self.resource_type + '_1',
                              'resource_id': self.resource_id},
                             {'action_id': 'new',
                              'resource_type': self.resource_type + '_1'}]

        self.resource.readl_scope_id.assert_not_called()
        self.resource_1.readl_scope_id.assert_not_called()
        self.backend.client.batch_verify_resources_perms.assert_called_once_with(principal_type=self.principal_type,
                                                                                 principal_id=self.principal_id,
                                                                                 scope_type=self.scope_type + '_1',
                                                                                 scope_id=self.scope_id,
                                                                                 resources_actions=resources_actions)

    @patch(BACKEND_BKIAM_RESOURCE_ID_FOR, MagicMock(return_value=resource_id))
    @patch(BACKEND_UTILS_RESOURCE_ID_FOR, MagicMock(return_value=resource_id))
    def test_verify_multiple_resource_perms__without_scope_id(self):
        perms_tuples = [(self.resource, ['new', 'view'], self.instance),
                        (self.resource, ['new'], None),
                        (self.resource_1, ['new', 'edit'], self.instance_1),
                        (self.resource_1, ['new'], self.instance_1)]

        self.backend.verify_multiple_resource_perms(principal_type=self.principal_type,
                                                    principal_id=self.principal_id,
                                                    perms_tuples=perms_tuples)

        resources_actions = [{'action_id': 'new',
                              'resource_type': self.resource_type},
                             {'action_id': 'view',
                              'resource_type': self.resource_type,
                              'resource_id': self.resource_id},
                             {'action_id': 'new',
                              'resource_type': self.resource_type},
                             {'action_id': 'new',
                              'resource_type': self.resource_type + '_1'},
                             {'action_id': 'edit',
                              'resource_type': self.resource_type + '_1',
                              'resource_id': self.resource_id},
                             {'action_id': 'new',
                              'resource_type': self.resource_type + '_1'}]

        self.resource.readl_scope_id.assert_not_called()
        self.resource_1.readl_scope_id.assert_not_called()
        self.backend.client.batch_verify_resources_perms.assert_called_once_with(principal_type=self.principal_type,
                                                                                 principal_id=self.principal_id,
                                                                                 scope_type=self.scope_type + '_1',
                                                                                 scope_id=self.real_scope_id,
                                                                                 resources_actions=resources_actions)

    def test_search_authorized_resources__with_scope_id(self):
        self.backend.search_authorized_resources(resource=self.resource,
                                                 principal_type=self.principal_type,
                                                 principal_id=self.principal_id,
                                                 action_ids=self.action_ids,
                                                 scope_id=self.scope_id)

        actions = [{'action_id': action_id, 'resource_type': self.resource_type} for action_id in self.action_ids]

        self.resource.real_scope_id.assert_not_called()
        self.backend.client.search_authorized_resources.assert_called_once_with(principal_type=self.principal_type,
                                                                                principal_id=self.principal_id,
                                                                                scope_type=self.scope_type,
                                                                                scope_id=self.scope_id,
                                                                                resource_types_actions=actions,
                                                                                resource_data_type='array',
                                                                                is_exact_resource=True)

    def test_search_authorized_resources__without_scope_id(self):
        self.backend.search_authorized_resources(resource=self.resource,
                                                 principal_type=self.principal_type,
                                                 principal_id=self.principal_id,
                                                 action_ids=self.action_ids)

        actions = [{'action_id': action_id, 'resource_type': self.resource_type} for action_id in self.action_ids]

        self.resource.real_scope_id.assert_called_once_with(None, None)
        self.backend.client.search_authorized_resources.assert_called_once_with(principal_type=self.principal_type,
                                                                                principal_id=self.principal_id,
                                                                                scope_type=self.scope_type,
                                                                                scope_id=self.real_scope_id,
                                                                                resource_types_actions=actions,
                                                                                resource_data_type='array',
                                                                                is_exact_resource=True)

    @patch(BACKEND_BKIAM_RESOURCE_ID_FOR, MagicMock(return_value=resource_id))
    @patch(BACKEND_UTILS_RESOURCE_ID_FOR, MagicMock(return_value=resource_id))
    def test_search_resources_perms_principals__with_scope_id(self):
        resources_actions_param = [{'action_id': 'new',
                                    'resource_type': self.resource_type},
                                   {'action_id': 'view',
                                    'resource_type': self.resource_type,
                                    'instance': self.instance},
                                   {'action_id': 'edit',
                                    'resource_type': self.resource_type,
                                    'instance': self.instance}]

        self.backend.search_resources_perms_principals(resource=self.resource,
                                                       resources_actions=resources_actions_param,
                                                       scope_id=self.scope_id)

        resources_actions = [{'action_id': 'new',
                              'resource_type': self.resource_type},
                             {'action_id': 'view',
                              'resource_type': self.resource_type,
                              'resource_id': self.resource_id},
                             {'action_id': 'edit',
                              'resource_type': self.resource_type,
                              'resource_id': self.resource_id}]

        self.resource.real_resource_id.assert_not_called()
        self.backend.client.search_resources_perms_principals.assert_called_once_with(
            scope_type=self.scope_type,
            scope_id=self.scope_id,
            resources_actions=resources_actions)

    @patch(BACKEND_BKIAM_RESOURCE_ID_FOR, MagicMock(return_value=resource_id))
    @patch(BACKEND_UTILS_RESOURCE_ID_FOR, MagicMock(return_value=resource_id))
    def test_search_resources_perms_principals__without_scope_id(self):
        resources_actions_param = [{'action_id': 'new',
                                    'resource_type': self.resource_type},
                                   {'action_id': 'view',
                                    'resource_type': self.resource_type,
                                    'instance': self.instance},
                                   {'action_id': 'edit',
                                    'resource_type': self.resource_type,
                                    'instance': self.instance}]

        self.backend.search_resources_perms_principals(resource=self.resource,
                                                       resources_actions=resources_actions_param)

        resources_actions = [{'action_id': 'new',
                              'resource_type': self.resource_type},
                             {'action_id': 'view',
                              'resource_type': self.resource_type,
                              'resource_id': self.resource_id},
                             {'action_id': 'edit',
                              'resource_type': self.resource_type,
                              'resource_id': self.resource_id}]

        self.resource.real_scope_id.assert_called_once_with(None, None)
        self.backend.client.search_resources_perms_principals.assert_called_once_with(
            scope_type=self.scope_type,
            scope_id=self.real_scope_id,
            resources_actions=resources_actions)
