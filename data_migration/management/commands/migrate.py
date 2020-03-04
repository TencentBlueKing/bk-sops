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

import sys

from django.conf import settings
from django.db import connections
from django.core.management.commands import migrate
from django.db.migrations.recorder import MigrationRecorder
from django.utils.module_loading import import_module


class Command(migrate.Command):

    def handle(self, *args, **options):
        # check if auth is not finish migrations
        db = options['database']
        connection = connections[db]

        is_auth_finish = False

        recorder = MigrationRecorder(connection)
        applied = recorder.applied_migrations()
        for migration in applied:

            if migration[0] == 'auth' and migration[1].startswith('0007'):
                is_auth_finish = True

        if settings.RUN_VER == 'open' and not is_auth_finish:
            sys.stdout.write('modify blueapps.account.0001_initial dependency.\n')
            first_migration_module = import_module("blueapps.account.migrations.0001_initial")
            first_migration_module.dependency = [
                ('auth', '0006_require_contenttypes_0002'),
            ]

        super(Command, self).handle(*args, **options)
