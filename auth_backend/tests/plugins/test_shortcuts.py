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

from mock import MagicMock, patch, call
from django.test import TestCase

from auth_backend.plugins import shortcuts
from auth_backend.exceptions import AuthFailedException, AuthBackendError

from auth_backend.tests.mock_path import *  # noqa


class ShortcutsTestCase(TestCase):
    permissions = 'permissions_token'

    def setUp(self):
        self.principal_type = 'principal_type_token'
        self.principal_id = 'principal_id_token'
        self.perms_tuples = []
        self.scope_id = 'scope_id_token'
        self.status = 'status_token'
        self.resource = 'resource_token'
        self.action_ids = 'action_ids_token'
        self.instance = 'instance_token'
        self.backend = MagicMock()

    @patch(SHORTCUTS_VERIFY_OR_RETURN_PERMS, MagicMock(return_value=[]))
    def test_batch_verify_or_raise_auth_failed__pass(self):
        shortcuts.batch_verify_or_raise_auth_failed(principal_type=self.principal_type,
                                                    principal_id=self.principal_id,
                                                    perms_tuples=self.perms_tuples,
                                                    scope_id=self.scope_id,
                                                    status=self.status)

        shortcuts.verify_or_return_insufficient_perms.assert_called_once_with(self.principal_type,
                                                                              self.principal_id,
                                                                              self.perms_tuples,
                                                                              self.scope_id)

    @patch(SHORTCUTS_VERIFY_OR_RETURN_PERMS, MagicMock(return_value=permissions))
    def test_batch_verify_or_raise_auth_failed__failed(self):
        try:
            shortcuts.batch_verify_or_raise_auth_failed(principal_type=self.principal_type,
                                                        principal_id=self.principal_id,
                                                        perms_tuples=self.perms_tuples,
                                                        scope_id=self.scope_id,
                                                        status=self.status)
        except AuthFailedException as e:
            self.assertEqual(e.permissions, self.permissions)
            self.assertEqual(e.status, self.status)

        shortcuts.verify_or_return_insufficient_perms.assert_called_once_with(self.principal_type,
                                                                              self.principal_id,
                                                                              self.perms_tuples,
                                                                              self.scope_id)

    @patch(SHORTCUTS_VERIFY_OR_RETURN_PERMS, MagicMock(return_value=[]))
    def test_verify_or_raise_auth_failed__pass(self):
        shortcuts.verify_or_raise_auth_failed(principal_type=self.principal_type,
                                              principal_id=self.principal_id,
                                              resource=self.resource,
                                              action_ids=self.action_ids,
                                              instance=self.instance,
                                              scope_id=self.scope_id,
                                              status=self.status)

        shortcuts.verify_or_return_insufficient_perms \
            .assert_called_once_with(self.principal_type,
                                     self.principal_id,
                                     [(self.resource, self.action_ids, self.instance)],
                                     self.scope_id)

    @patch(SHORTCUTS_VERIFY_OR_RETURN_PERMS, MagicMock(return_value=permissions))
    def test_verify_or_raise_auth_failed__failed(self):
        try:
            shortcuts.verify_or_raise_auth_failed(principal_type=self.principal_type,
                                                  principal_id=self.principal_id,
                                                  resource=self.resource,
                                                  action_ids=self.action_ids,
                                                  instance=self.instance,
                                                  scope_id=self.scope_id,
                                                  status=self.status)
        except AuthFailedException as e:
            self.assertEqual(e.permissions, self.permissions)
            self.assertEqual(e.status, self.status)

        shortcuts.verify_or_return_insufficient_perms \
            .assert_called_once_with(self.principal_type,
                                     self.principal_id,
                                     [(self.resource, self.action_ids, self.instance)],
                                     self.scope_id)

    def test_verify_or_return_insufficient_perms__backend_error(self):
        self.backend.verify_multiple_resource_perms = MagicMock(return_value={'result': False, 'message': 'message'})
        patcher = patch(SHORTCUTS_GET_BACKEND_FROM_CONFIG, MagicMock(return_value=self.backend))
        patcher.start()

        self.assertRaises(AuthBackendError,
                          shortcuts.verify_or_return_insufficient_perms,
                          principal_type=self.principal_type,
                          principal_id=self.principal_id,
                          perms_tuples=self.perms_tuples,
                          scope_id=self.scope_id)

        self.backend.verify_multiple_resource_perms.assert_called_once_with(self.principal_type,
                                                                            self.principal_id,
                                                                            self.perms_tuples,
                                                                            self.scope_id)

        patcher.stop()

    def test_verify_or_return_insufficient_perms__all_pass(self):
        data = [{'is_pass': True},
                {'is_pass': True},
                {'is_pass': True}]
        self.backend.verify_multiple_resource_perms = MagicMock(return_value={'result': True, 'data': data})
        patcher = patch(SHORTCUTS_GET_BACKEND_FROM_CONFIG, MagicMock(return_value=self.backend))
        patcher.start()

        permissions = shortcuts.verify_or_return_insufficient_perms(principal_type=self.principal_type,
                                                                    principal_id=self.principal_id,
                                                                    perms_tuples=self.perms_tuples,
                                                                    scope_id=self.scope_id)

        self.assertEqual(permissions, [])
        self.backend.verify_multiple_resource_perms.assert_called_once_with(self.principal_type,
                                                                            self.principal_id,
                                                                            self.perms_tuples,
                                                                            self.scope_id)

        patcher.stop()

    @patch(SHORTCUTS_BUILD_NEED_PERMISSION, MagicMock(return_value=permissions))
    def test_verify_or_return_insufficient_perms__auth_failed(self):
        data = [{'is_pass': True},
                {'is_pass': False,
                 'action_id': 'action_1',
                 'resource_type': 'resource_1',
                 'resource_id': [{'resource_type': 'resource_1', 'resource_id': 'resource_1_id'}]},
                {'is_pass': False,
                 'action_id': 'action_2',
                 'resource_type': 'resource_2',
                 'resource_id': [{'resource_type': 'resource_1', 'resource_id': 'resource_1_id'},
                                 {'resource_type': 'resource_2', 'resource_id': 'resource_2_id'}]},
                {'is_pass': False,
                 'action_id': 'action_3',
                 'resource_type': 'resource_3',
                 'resource_id': []}]

        lib = {'resource_1': 'resource_1_type',
               'resource_2': 'resource_2_type',
               'resource_3': 'resource_3_type'}

        self.backend.verify_multiple_resource_perms = MagicMock(return_value={'result': True, 'data': data})
        patcher_1 = patch(SHORTCUTS_GET_BACKEND_FROM_CONFIG, MagicMock(return_value=self.backend))
        patcher_2 = patch(SHORTCUTS_RESOURCE_TYPE_LIB, lib)
        patcher_1.start()
        patcher_2.start()

        permissions = shortcuts.verify_or_return_insufficient_perms(principal_type=self.principal_type,
                                                                    principal_id=self.principal_id,
                                                                    perms_tuples=self.perms_tuples,
                                                                    scope_id=self.scope_id)

        self.assertEqual(permissions, [self.permissions, self.permissions, self.permissions])
        self.backend.verify_multiple_resource_perms.assert_called_once_with(self.principal_type,
                                                                            self.principal_id,
                                                                            self.perms_tuples,
                                                                            self.scope_id)

        shortcuts.build_need_permission.assert_has_calls([
            call(auth_resource=lib['resource_1'], action_id='action_1', instance='resource_1_id',
                 scope_id=self.scope_id),
            call(auth_resource=lib['resource_2'], action_id='action_2', instance='resource_2_id',
                 scope_id=self.scope_id),
            call(auth_resource=lib['resource_3'], action_id='action_3', instance=None,
                 scope_id=self.scope_id)
        ])

        patcher_1.stop()
        patcher_2.stop()
