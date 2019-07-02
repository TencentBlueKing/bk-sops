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

from django.test import TestCase
from mock import MagicMock

from auth_backend.resources.migrations.migration import BKIAMResourceMigration
from auth_backend.resources.migrations.exceptions import MigrationOperationFailedError


class BKIAMResourceMigrationTestCase(TestCase):

    def setUp(self):
        self.call_data = {'a': 'a', 'b': 'b'}

    def test_apply(self):
        operations = [
            {
                'operation': 'a',
                'data': {'a': 'a'}
            },
            {
                'operation': 'b',
                'data': {'b': 'b'}
            },
            {
                'operation': 'c',
                'data': {'c': 'c'}
            }
        ]
        migration = BKIAMResourceMigration(operations)
        for op in operations:
            setattr(migration, op['operation'], MagicMock())

        migration.apply()

        for op in operations:
            getattr(migration, op['operation']).assert_called_once_with(op['data'])

    def test_register_system(self):
        migration = BKIAMResourceMigration({})
        migration.client = MagicMock()
        migration.client.register_system = MagicMock(return_value={'result': True})

        migration.register_system(self.call_data)

        migration.client.register_system.assert_called_once_with(**self.call_data)

        migration.client.register_system = MagicMock(return_value={'result': False,
                                                                   'code': migration.SYSTEM_EXIST_CODE})

        migration.register_system(self.call_data)

        migration.client.register_system.assert_called_once_with(**self.call_data)

    def test_register_system__raise_error(self):
        migration = BKIAMResourceMigration({})
        migration.client = MagicMock()
        migration.client.register_system = MagicMock(return_value={'result': False,
                                                                   'message': ''})

        self.assertRaises(MigrationOperationFailedError, migration.register_system, self.call_data)

    def test_batch_upsert_resource_types(self):
        migration = BKIAMResourceMigration({})
        migration.client = MagicMock()
        migration.client.batch_upsert_resource_types = MagicMock(return_value={'result': True})

        migration.batch_upsert_resource_types(self.call_data)

        migration.client.batch_upsert_resource_types.assert_called_once_with(**self.call_data)

    def test_batch_upsert_resource_types__raise_error(self):
        migration = BKIAMResourceMigration({})
        migration.client = MagicMock()
        migration.client.batch_upsert_resource_types = MagicMock(return_value={'result': False,
                                                                               'message': ''})

        self.assertRaises(MigrationOperationFailedError, migration.batch_upsert_resource_types, self.call_data)

    def test_delete_resource_type(self):
        migration = BKIAMResourceMigration({})
        migration.client = MagicMock()
        migration.client.delete_resource_type = MagicMock(return_value={'result': True})

        migration.delete_resource_type(self.call_data)

        migration.client.delete_resource_type.assert_called_once_with(**self.call_data)

        migration.client.delete_resource_type = MagicMock(return_value={'result': False,
                                                                        'code': migration.RESOURCE_NOT_EXIST_CODE})

        migration.delete_resource_type(self.call_data)

        migration.client.delete_resource_type.assert_called_once_with(**self.call_data)

    def test_delete_resource_type__raise_error(self):
        migration = BKIAMResourceMigration({})
        migration.client = MagicMock()
        migration.client.delete_resource_type = MagicMock(return_value={'result': False,
                                                                        'message': ''})

        self.assertRaises(MigrationOperationFailedError, migration.delete_resource_type, self.call_data)
