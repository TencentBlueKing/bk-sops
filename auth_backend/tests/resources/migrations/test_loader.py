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

from auth_backend.resources.migrations.loader import ResourceMigrationLoader
from auth_backend.tests.mock_path import *  # noqa


class ResourceMigrationLoaderTestCase(TestCase):
    def setUp(self):
        mock_loader = MagicMock()
        mock_loader.disk_migrations = [('a', ''), ('b', '')]

        self.loader = ResourceMigrationLoader()
        self.loader._loader = mock_loader

    def test_is_first_make(self):
        with patch(LOADER_APP_LABEL, 'c'):
            self.assertTrue(self.loader.is_first_make())

        with patch(LOADER_APP_LABEL, 'a'):
            self.assertFalse(self.loader.is_first_make())

    def test_last_migration(self):
        last_migration_info = ('a', 'b')
        last_migration_return = 'TOKEN'
        self.loader._loader.graph = MagicMock()
        self.loader._loader.graph.leaf_nodes = MagicMock(return_value=[last_migration_info])
        self.loader._loader.get_migration = MagicMock(return_value=last_migration_return)

        self.assertEqual(self.loader.last_migration(), last_migration_return)
        self.loader._loader.get_migration.assert_called_once_with(*last_migration_info)

    def test_last_migration__return_none(self):
        self.loader._loader.graph = MagicMock()
        self.loader._loader.graph.leaf_nodes = MagicMock(return_value=[])

        self.assertIsNone(self.loader.last_migration())

    def test_last_migration__raise_error(self):
        self.loader._loader.graph = MagicMock()
        self.loader._loader.graph.leaf_nodes = MagicMock(return_value=[1, 2])

        self.assertRaises(LookupError, self.loader.last_migration)
