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

from mock import MagicMock, patch, call

from django.test import TestCase

from auth_backend.resources.django import DjangoModelResource

from gcloud.contrib.auth.backend import utils
from gcloud.contrib.auth.backend import FreeAuthBackend

from gcloud.tests.mock_settings import *  # noqa


class TestResource(DjangoModelResource):
    pass


class FreeAuthBackendTestCase(TestCase):

    def setUp(self):
        self.backend = FreeAuthBackend()
        self.principal_type = 'principal_type_token'
        self.principal_id = 'principal_id_token'
        self.action_ids = ['1', '2', '3', '4']

    def test_register_instance(self):
        auth_result = self.backend.register_instance(resource=MagicMock(),
                                                     instance=MagicMock())

        self.assertEqual(auth_result, {'result': True,
                                       'code': 0,
                                       'message': 'success',
                                       'data': {}})

    def test_batch_register_instance(self):
        auth_result = self.backend.batch_register_instance(resource=MagicMock(),
                                                           instances=MagicMock())

        self.assertEqual(auth_result, {'result': True,
                                       'code': 0,
                                       'message': 'success',
                                       'data': {}})

    def test_update_instance(self):
        auth_result = self.backend.update_instance(resource=MagicMock(),
                                                   instance=MagicMock())

        self.assertEqual(auth_result, {'result': True,
                                       'code': 0,
                                       'message': 'success',
                                       'data': {}})

    def test_delete_instance(self):
        auth_result = self.backend.delete_instance(resource=MagicMock(),
                                                   instance=MagicMock())

        self.assertEqual(auth_result, {'result': True,
                                       'code': 0,
                                       'message': 'success',
                                       'data': {}})

    def test_batch_delete_instance(self):
        auth_result = self.backend.batch_delete_instance(resource=MagicMock(),
                                                         instances=MagicMock())

        self.assertEqual(auth_result, {'result': True,
                                       'code': 0,
                                       'message': 'success',
                                       'data': {}})

    @patch(GCLOUD_CONTRIB_AUTH_BACKEND_UTILS_RESOURCE_ACTIONS_FOR, MagicMock(return_value=[{}]))
    def test_verify_perms_with_none_instance(self):
        resource = MagicMock()
        auth_result = self.backend.verify_perms(principal_type=self.principal_type,
                                                principal_id=self.principal_id,
                                                resource=resource,
                                                action_ids=self.action_ids)

        self.assertEqual(auth_result, {'result': True,
                                       'code': 0,
                                       'message': 'success',
                                       'data': [{'is_pass': True}]})

        utils.resource_actions_for.assert_called_once_with(resource=resource,
                                                           action_ids=self.action_ids,
                                                           instances=[],
                                                           ignore_relate_instance_act=False)

    @patch(GCLOUD_CONTRIB_AUTH_BACKEND_UTILS_RESOURCE_ACTIONS_FOR, MagicMock(return_value=[{}]))
    def test_verify_perms_with_instance(self):
        resource = MagicMock()
        instance = MagicMock()
        auth_result = self.backend.verify_perms(principal_type=self.principal_type,
                                                principal_id=self.principal_id,
                                                resource=resource,
                                                action_ids=self.action_ids,
                                                instance=instance)

        self.assertEqual(auth_result, {'result': True,
                                       'code': 0,
                                       'message': 'success',
                                       'data': [{'is_pass': True}]})

        utils.resource_actions_for.assert_called_once_with(resource=resource,
                                                           action_ids=self.action_ids,
                                                           instances=[instance],
                                                           ignore_relate_instance_act=False)

    @patch(GCLOUD_CONTRIB_AUTH_BACKEND_UTILS_RESOURCE_ACTIONS_FOR, MagicMock(return_value=[{}]))
    def test_batch_verify_perms_with_none_instance(self):
        resource = MagicMock()
        auth_result = self.backend.batch_verify_perms(principal_type=self.principal_type,
                                                      principal_id=self.principal_id,
                                                      resource=resource,
                                                      action_ids=self.action_ids)

        self.assertEqual(auth_result, {'result': True,
                                       'code': 0,
                                       'message': 'success',
                                       'data': [{'is_pass': True}]})

        utils.resource_actions_for.assert_called_once_with(resource=resource,
                                                           action_ids=self.action_ids,
                                                           instances=[],
                                                           ignore_relate_instance_act=False)

    @patch(GCLOUD_CONTRIB_AUTH_BACKEND_UTILS_RESOURCE_ACTIONS_FOR, MagicMock(return_value=[{}]))
    def test_batch_verify_perms_with_instances(self):
        resource = MagicMock()
        instances = [MagicMock()]
        auth_result = self.backend.batch_verify_perms(principal_type=self.principal_type,
                                                      principal_id=self.principal_id,
                                                      resource=resource,
                                                      action_ids=self.action_ids,
                                                      instances=instances)

        self.assertEqual(auth_result, {'result': True,
                                       'code': 0,
                                       'message': 'success',
                                       'data': [{'is_pass': True}]})

        utils.resource_actions_for.assert_called_once_with(resource=resource,
                                                           action_ids=self.action_ids,
                                                           instances=instances,
                                                           ignore_relate_instance_act=False)

    @patch(GCLOUD_CONTRIB_AUTH_BACKEND_UTILS_RESOURCE_ACTIONS_FOR, MagicMock(return_value=[{}]))
    def test_verify_multiple_resource_perms(self):
        resource_1 = MagicMock()
        resource_2 = MagicMock()
        instance_1 = MagicMock()
        instance_2 = None
        perms_tuples = [(resource_1, self.action_ids, instance_1),
                        (resource_2, self.action_ids, instance_2)]

        auth_result = self.backend.verify_multiple_resource_perms(principal_type=self.principal_type,
                                                                  principal_id=self.principal_id,
                                                                  perms_tuples=perms_tuples)

        self.assertEqual(auth_result, {'result': True,
                                       'code': 0,
                                       'message': 'success',
                                       'data': [{'is_pass': True},
                                                {'is_pass': True}]})

        utils.resource_actions_for.assert_has_calls([call(resource=resource_1,
                                                          action_ids=self.action_ids,
                                                          instances=[instance_1],
                                                          ignore_relate_instance_act=False),
                                                     call(resource=resource_2,
                                                          action_ids=self.action_ids,
                                                          instances=None,
                                                          ignore_relate_instance_act=False)
                                                     ])

    def test_search_authorized_resources_raise_not_implemented(self):
        self.assertRaises(NotImplementedError, self.backend.search_authorized_resources,
                          resource=MagicMock(),
                          principal_type=self.principal_type,
                          principal_id=self.principal_id,
                          action_ids=self.action_ids)

    @patch(GCLOUD_CONTRIB_AUTH_BACKEND_UTILS_RESOURCE_ACTIONS_FOR, MagicMock(return_value=[{}]))
    def test_search_authorized_resources(self):
        ids = ['1', '2', '3']
        mock_qs = MagicMock()
        mock_qs.values_list = MagicMock(return_value=ids)

        resource = TestResource(
            rtype='test_resource',
            name='test_resource',
            scope_type='system',
            scope_id='test_scope',
            scope_name='test scope',
            actions=[],
            operations=[],
            inspect=None,
            id_field='id',
            resource_cls=MagicMock())
        resource.resource_cls.objectest_search_authorized_resourcests = MagicMock()
        resource.resource_cls.objects.all = MagicMock(return_value=mock_qs)

        auth_result = self.backend.search_authorized_resources(resource=resource,
                                                               principal_type=self.principal_type,
                                                               principal_id=self.principal_id,
                                                               action_ids=self.action_ids)

        self.assertEqual(auth_result, {'result': True,
                                       'code': 0,
                                       'message': 'success',
                                       'data': [{'resource_ids': [
                                           [{'resource_type': 'test_resource', 'resource_id': '1'}],
                                           [{'resource_type': 'test_resource', 'resource_id': '2'}],
                                           [{'resource_type': 'test_resource', 'resource_id': '3'}]]}]})

        utils.resource_actions_for.assert_called_once_with(resource=resource,
                                                           action_ids=self.action_ids,
                                                           instances=[],
                                                           ignore_relate_instance_act=False)

    @patch(GCLOUD_CONTRIB_AUTH_BACKEND_UTILS_RESOURCE_ID_FOR, MagicMock(return_value='instance_id'))
    def test_search_resources_perms_principals(self):
        resource = MagicMock()
        resource.rtype = 'resource_type_token'
        action_id_1 = 'action_id_1'
        action_id_2 = 'action_id_2'
        instance = MagicMock()

        ids = ['1', '2', '3']
        mock_qs = MagicMock()
        mock_qs.values_list = MagicMock(return_value=ids)
        user_model = MagicMock()
        user_model.objects = MagicMock()
        user_model.objects.all = MagicMock(return_value=mock_qs)

        principals = [{'principal_type': 'user', 'principal_id': uid} for uid in ids]

        with patch(GCLOUD_CONTRIB_AUTH_BACKEND_GET_USER_MODEL, MagicMock(return_value=user_model)):
            auth_result = self.backend.search_resources_perms_principals(resource=resource,
                                                                         resources_actions=[
                                                                             {'action_id': action_id_1,
                                                                              'instance': None},
                                                                             {'action_id': action_id_2,
                                                                              'instance': instance}])

            self.assertEqual(auth_result, {'result': True,
                                           'code': 0,
                                           'message': 'success',
                                           'data': [{'action_id': 'action_id_1',
                                                     'resource_type': resource.rtype,
                                                     'principals': principals},
                                                    {'action_id': 'action_id_2',
                                                     'resource_type': resource.rtype,
                                                     'resource_id': 'instance_id',
                                                     'principals': principals}
                                                    ]})
