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

from datetime import datetime

from django.conf import settings
from django.core.management.base import BaseCommand

from auth_backend.constants import APP_LABEL
from auth_backend.resources.migrations.differ import SnapshotDiffer
from auth_backend.resources.migrations.snapper import ResourceStateSnapper
from auth_backend.resources.migrations.loader import ResourceMigrationLoader
from auth_backend.resources.migrations.finder import (
    ResourceSnapshotReader,
    ResourceSnapshotWriter,
    MigrationWriter,
)


class Command(BaseCommand):
    help = "Creates new migration for perms model"

    def handle(self, *args, **options):
        # take snapshot
        snapper = ResourceStateSnapper()
        snapshot = snapper.take_snapshot()

        # check whether is first make migrations
        loader = ResourceMigrationLoader()

        is_first_make = loader.is_first_make()
        last_migration = None

        # check snapshot equality if is not first make
        if not is_first_make:
            last_migration = loader.last_migration()
            reader = ResourceSnapshotReader(last_migration.snapshot_json)
            last_snapshot = reader.read()
            differ = SnapshotDiffer(last_snapshot=last_snapshot, snapshot=snapshot)

            if not differ.has_change():
                self.stdout.write("No changes detected")
                return

        # write snapshot json and migration py
        self.write_migration_files(last_migration, snapshot)

    def write_migration_files(self, last_migration, snapshot):

        migration_name, snapshot_name = self.operation_names(last_migration)

        snapshot_writer = ResourceSnapshotWriter(snapshot_name=snapshot_name, snapshot=snapshot)
        migration_writer = MigrationWriter(migration_name=migration_name,
                                           snapshot_name=snapshot_name,
                                           last_migration=last_migration,
                                           app_label=APP_LABEL)

        snapshot_writer.write()
        migration_writer.write()
        self.stdout.write('Perms migrations:')
        self.stdout.write('  %s' % snapshot_writer.path)
        self.stdout.write('  %s' % migration_writer.path)

    def operation_names(self, last_migration):
        system_id = getattr(settings, 'BK_IAM_SYSTEM_ID', None)
        time = datetime.now().strftime('%Y%m%d%H%M')

        if not system_id:
            self.stdout.write("You must set BK_IAM_SYSTEM_ID in django settings before make migrations")
            return

        if not last_migration:
            return '0001_initial', \
                   '0001_{system_id}_{time}'.format(system_id=system_id, time=time)

        code = '%04d' % (int(last_migration.name[:4]) + 1)

        return '{code}_{time}'.format(code=code, time=time), \
               '{code}_{system_id}_{time}'.format(code=code, system_id=system_id, time=time)
