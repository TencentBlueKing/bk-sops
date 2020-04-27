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

import ujson as json
from django.test import TestCase
from mock import MagicMock, call, patch

from auth_backend.contrib.consistency.models import RegisterFailInstanceArchive

from ..mock_path import *  # noqa


class RegisterFailInstanceArchiveTestCase(TestCase):

    def setUp(self):
        self.resource = MagicMock()
        self.resource.rtype = 'resource_type_token'
        self.resource.resource_id = MagicMock(return_value='instance_id')
        self.instance = 'instance_token'
        self.instances = ['token_1', 'token_2', 'token_3']
        self.scope_id = 'scope_id_token'

    def test_record_fail_register(self):
        archive = RegisterFailInstanceArchive.objects.record_fail_register(
            resource=self.resource,
            instance=self.instance,
            scope_id=self.scope_id
        )

        self.assertEqual(archive.resource_type, self.resource.rtype)
        self.assertEqual(archive.instances, '["instance_id"]')
        self.assertEqual(archive.scope_id, self.scope_id)
        self.resource.resource_id.assert_called_once_with(self.instance)

    def test_record_fail_register__with_none_scope_id(self):
        archive = RegisterFailInstanceArchive.objects.record_fail_register(
            resource=self.resource,
            instance=self.instance,
            scope_id=None
        )

        self.assertEqual(archive.resource_type, self.resource.rtype)
        self.assertEqual(archive.instances, '["instance_id"]')
        self.assertEqual(archive.scope_id, '')
        self.resource.resource_id.assert_called_once_with(self.instance)

    def test_record_fail_batch_register(self):
        archive = RegisterFailInstanceArchive.objects.record_fail_batch_register(
            resource=self.resource,
            instances=self.instances,
            scope_id=self.scope_id
        )

        self.assertEqual(archive.resource_type, self.resource.rtype)
        self.assertEqual(archive.instances, '["instance_id","instance_id","instance_id"]')
        self.assertEqual(archive.scope_id, self.scope_id)
        self.resource.resource_id.assert_has_calls([call(inst) for inst in self.instances])

    def test_record_fail_batch_register__with_none_scope_id(self):
        archive = RegisterFailInstanceArchive.objects.record_fail_batch_register(
            resource=self.resource,
            instances=self.instances,
            scope_id=None
        )

        self.assertEqual(archive.resource_type, self.resource.rtype)
        self.assertEqual(archive.instances, '["instance_id","instance_id","instance_id"]')
        self.assertEqual(archive.scope_id, '')
        self.resource.resource_id.assert_has_calls([call(inst) for inst in self.instances])

    def test_register(self):
        archive = RegisterFailInstanceArchive.objects.record_fail_register(
            resource=self.resource,
            instance=self.instance,
            scope_id=self.scope_id
        )
        archive.delete = MagicMock()

        with patch(CONSISTENCY_MODELS_RESOURCE_TYPE_LIB, {'resource_type_token': self.resource}):

            archive.register()
            self.resource.batch_register_instance.assert_called_once_with(
                instances=json.loads(archive.instances),
                scope_id=archive.scope_id
            )
            archive.delete.assert_called_once()
