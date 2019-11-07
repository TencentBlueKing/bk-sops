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

from builtins import object
from django.db.migrations.loader import MigrationLoader

from auth_backend.constants import APP_LABEL


class ResourceMigrationLoader(object):

    def __init__(self):
        self._loader = MigrationLoader(None, ignore_no_migrations=True)

    def is_first_make(self):
        migration_app_labels = {migration_tuple[0] for migration_tuple in self._loader.disk_migrations}
        return APP_LABEL not in migration_app_labels

    def last_migration(self):
        leaf_migrations = self._loader.graph.leaf_nodes(APP_LABEL)

        if not leaf_migrations:
            return None

        if len(leaf_migrations) > 1:
            raise LookupError('Found multiple leaf migrations: %s' % leaf_migrations)

        last_migration_info = leaf_migrations[0]

        return self._loader.get_migration(*last_migration_info)
