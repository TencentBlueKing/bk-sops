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

import os
import sys

from django.conf import settings
from django.db import connections
from django.core.management.commands import migrate
from django.db.migrations.recorder import MigrationRecorder


class Command(migrate.Command):

    def handle(self, *args, **options):
        # check if auth is not finish migrations
        db = options['database']
        connection = connections[db]

        recorder = MigrationRecorder(connection)
        applied = recorder.applied_migrations()

        if applied:
            is_auth_finish = False
            target_init_path = os.path.join(
                settings.BASE_DIR, 'blueapps', 'account', 'migrations', '__init__.py')
            target_init_pyc_path = os.path.join(
                settings.BASE_DIR, 'blueapps', 'account', 'migrations', '__init__.pyc')

            for migration in applied:

                if migration[0] == 'auth' and migration[1].startswith('0007'):
                    is_auth_finish = True

            if settings.RUN_VER == 'open' and not is_auth_finish:
                sys.stdout.write('remove init for auth is not finish.\n')
                try:
                    os.remove(target_init_path)
                    os.remove(target_init_pyc_path)
                except FileNotFoundError:
                    pass

                sys.stdout.write('ready to execute the true migrate\n')
                super(Command, self).handle(*args, **options)

                if not is_auth_finish:
                    open(target_init_path, 'w')
                    sys.stdout.write('ready to execute the true migrate again\n')

        super(Command, self).handle(*args, **options)
