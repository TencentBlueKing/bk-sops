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

from django.test import TestCase
from mock import MagicMock, patch

from auth_backend.resources.migrations.migration import (
    ResourceMigration,
    DummyResourceMigration,
    settings
)
from auth_backend.tests.mock_path import *  # noqa


class ResourceMigrationTestCase(TestCase):

    def setUp(self):
        self.diff_operations = 'TOKEN'
        settings.AUTH_BACKEND_RESOURCE_MIGRATION_CLASS = None

    def tearDown(self):
        delattr(settings, 'AUTH_BACKEND_RESOURCE_MIGRATION_CLASS')

    def test_get_migration(self):
        with patch(MIGRATION_MIGRATION_CLASS, None):
            migration = ResourceMigration.get_migration(self.diff_operations)
            self.assertTrue(isinstance(migration, DummyResourceMigration))

        migration_class = 'CLASS_TOKEN'
        import_string_return = MagicMock()
        import_string = MagicMock(return_value=import_string_return)
        with patch(MIGRATION_MIGRATION_CLASS, migration_class):
            with patch(MIGRATION_IMPORT_STRING, import_string):
                ResourceMigration.get_migration(self.diff_operations)

                import_string.assert_called_once_with(migration_class)
                import_string_return.assert_called_once_with(self.diff_operations)
