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

from django.db import migrations
from django.db.migrations.loader import MigrationLoader

from auth_backend.resources.migrations import ResourceMigration
from auth_backend.resources.migrations.finder import ResourceSnapshotReader
from auth_backend.resources.migrations.differ import SnapshotDiffer


def forward_func(apps, schema_editor):
    reader = ResourceSnapshotReader(Migration.snapshot_json)
    snapshot = reader.read()
    last_snapshot = None

    if Migration.dependencies:
        loader = MigrationLoader(None, ignore_no_migrations=True)
        last_migration = loader.disk_migrations[Migration.dependencies[0]]
        last_reader = ResourceSnapshotReader(last_migration.snapshot_json)
        last_snapshot = last_reader.read()

    differ = SnapshotDiffer(last_snapshot, snapshot)
    operations = differ.diff_operations()

    migration = ResourceMigration.get_migration(operations)

    migration.apply()


class Migration(migrations.Migration):
    snapshot_json = '0002_bk_sops_201909061515'

    dependencies = [('auth_backend', '0001_initial')]

    operations = [
        migrations.RunPython(forward_func)
    ]
