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
from mock import MagicMock, call, patch

from auth_backend import exceptions
from auth_backend.contrib.consistency import legacy
from auth_backend.contrib.consistency.tests.mock_path import *  # noqa
from auth_backend.resources.interfaces import InstanceIterableResource


class ZeroInstanceResource(InstanceIterableResource):
    def count(self):
        pass

    def slice(self, start, end):
        pass


class ManyInstanceResource(InstanceIterableResource):
    def count(self):
        pass

    def slice(self, start, end):
        pass


class LegacyTestCase(TestCase):

    @patch(LEGACY_RESOURCE_TYPE_LIB, {})
    def test_register_legacy_instances__raise_auth_lookup(self):
        self.assertRaises(exceptions.AuthLookupError,
                          legacy.register_legacy_instances,
                          ['not_exist_resource_1', 'not_exist_resource_2'])

    @patch(LEGACY_RESOURCE_TYPE_LIB, {'resource_1': 'token'})
    def test_register_legacy_instances__raise_auth_invalid_operation(self):
        self.assertRaises(exceptions.AuthInvalidOperationError,
                          legacy.register_legacy_instances,
                          ['resource_1', 'resource_2'])

    def test_register_legacy(self):
        resource_1 = ZeroInstanceResource()
        resource_2 = ManyInstanceResource()
        resource_3 = ManyInstanceResource()

        resource_1.count = MagicMock(return_value=0)
        resource_1.slice = MagicMock()
        resource_1.batch_register_instance = MagicMock()

        resource_2_slice = ['resource_2_token']
        resource_2.count = MagicMock(return_value=300)
        resource_2.slice = MagicMock(return_value=resource_2_slice)
        resource_2.batch_register_instance = MagicMock(return_value={'result': False,
                                                                     'code': legacy.AUTH_CONFLICT_CODE})

        resource_3_slice = ['resource_3_token']
        resource_3.count = MagicMock(return_value=434)
        resource_3.slice = MagicMock(return_value=resource_3_slice)
        resource_3.batch_register_instance = MagicMock(return_value={'result': True})

        resource_type_lib = {
            '1': resource_1,
            '2': resource_2,
            '3': resource_3
        }
        conf = MagicMock()
        conf.BATCH_REGISTER_SIZE = 100

        with patch(LEGACY_RESOURCE_TYPE_LIB, resource_type_lib):
            with patch(CONSISTENCY_LEGACY_CONF, conf):
                legacy.register_legacy_instances(['1', '3', '2'])

                resource_1.slice.assert_not_called()
                resource_1.batch_register_instance.assert_not_called()

                resource_2.slice.assert_has_calls([call(start=0, end=100),
                                                   call(start=100, end=200),
                                                   call(start=200, end=300),
                                                   call(start=300, end=400)])
                resource_2.batch_register_instance.assert_has_calls([call(resource_2_slice),
                                                                     call(resource_2_slice),
                                                                     call(resource_2_slice),
                                                                     call(resource_2_slice)])

                resource_3.slice.assert_has_calls([call(start=0, end=100),
                                                   call(start=100, end=200),
                                                   call(start=200, end=300),
                                                   call(start=300, end=400),
                                                   call(start=400, end=500)])
                resource_3.batch_register_instance.assert_has_calls([call(resource_3_slice),
                                                                     call(resource_3_slice),
                                                                     call(resource_3_slice),
                                                                     call(resource_3_slice),
                                                                     call(resource_3_slice)])
