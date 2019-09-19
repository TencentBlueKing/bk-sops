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

from mock import MagicMock
from django.test import TestCase

from auth_backend.plugins import utils

from auth_backend.tests.mock_path import *  # noqa


class UtilsTestCase(TestCase):

    def setUp(self):
        self.resource_type = 'resource_type_token'
        self.resource_type_name = 'resource_type_name_token'
        self.base_info = {
            'resource': {
                'resource_type': self.resource_type,
                'resource_type_name': self.resource_type_name
            },
            'base': 'base_token',
            'scope_id': 'base_scope_id_token'
        }
        self.action_id = 'action_id_token'
        self.action_name = 'action_name_token'
        self.instance = 'instance_token'
        self.scope_id = 'scope_id_token'
        self.resource_name = 'resource_name_token'
        self.resource_id = 'resource_id_token'

        self.instance_object = MagicMock()
        self.auth_resource = MagicMock()
        self.auth_resource.base_info = MagicMock(return_value=self.base_info)
        self.auth_resource.resource_id = MagicMock(return_value=self.resource_id)
        self.auth_resource.resource_name = MagicMock(return_value=self.resource_name)
        self.action = MagicMock()
        self.action.name = self.action_name
        self.auth_resource.actions_map = {
            self.action_id: self.action
        }

    def test_build_need_permission__with_none_instance(self):
        permission = utils.build_need_permission(auth_resource=self.auth_resource,
                                                 action_id=self.action_id,
                                                 scope_id=self.scope_id)
        expect_permission = {
            'base': 'base_token',
            'scope_id': self.scope_id,
            'action_id': self.action_id,
            'action_name': self.action_name,
            'resource_type': self.resource_type,
            'resource_type_name': self.resource_type_name,
            'resources': []
        }
        self.assertEqual(permission, expect_permission)

    def test_build_need_permission__with_none_scope_id(self):
        permission = utils.build_need_permission(auth_resource=self.auth_resource,
                                                 action_id=self.action_id)
        expect_permission = {
            'base': 'base_token',
            'scope_id': 'base_scope_id_token',
            'action_id': self.action_id,
            'action_name': self.action_name,
            'resource_type': self.resource_type,
            'resource_type_name': self.resource_type_name,
            'resources': []
        }
        self.assertEqual(permission, expect_permission)

    def test_build_need_permission__with_instance_object(self):
        permission = utils.build_need_permission(auth_resource=self.auth_resource,
                                                 action_id=self.action_id,
                                                 instance=self.instance_object,
                                                 scope_id=self.scope_id)

        expect_permission = {
            'base': 'base_token',
            'scope_id': 'scope_id_token',
            'action_id': self.action_id,
            'action_name': self.action_name,
            'resource_type': self.resource_type,
            'resource_type_name': self.resource_type_name,
            'resources': [
                [
                    {
                        'resource_type': self.resource_type,
                        'resource_type_name': self.resource_type_name,
                        'resource_id': self.resource_id,
                        'resource_name': self.resource_name
                    }
                ]
            ]
        }
        self.assertEqual(permission, expect_permission)
        self.auth_resource.resource_id.assert_called_once_with(self.instance_object)

    def test_build_need_permission__with_instance_id(self):
        permission = utils.build_need_permission(auth_resource=self.auth_resource,
                                                 action_id=self.action_id,
                                                 instance=self.instance,
                                                 scope_id=self.scope_id)

        expect_permission = {
            'base': 'base_token',
            'scope_id': 'scope_id_token',
            'action_id': self.action_id,
            'action_name': self.action_name,
            'resource_type': self.resource_type,
            'resource_type_name': self.resource_type_name,
            'resources': [
                [
                    {
                        'resource_type': self.resource_type,
                        'resource_type_name': self.resource_type_name,
                        'resource_id': self.instance,
                        'resource_name': self.resource_name
                    }
                ]
            ]
        }
        self.assertEqual(permission, expect_permission)
        self.auth_resource.resource_id.assert_not_called()
