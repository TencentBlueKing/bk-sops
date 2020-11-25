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
import codecs

from datetime import datetime

from django.conf import settings
from django.template.loader import render_to_string
from django.core.management.base import BaseCommand
from django.db.migrations.loader import MigrationLoader

from iam.contrib.iam_migration.apps import IAMMigrationConfig
from iam.contrib.iam_migration.conf import MIGRATION_TEMPLATE_NAME


class Command(BaseCommand):

    help = "Create new migration for specific iam migration json file e.g. python manage.py iam_makemigrations migration.json"

    def add_arguments(self, parser):
        parser.add_argument("migration_json", nargs="?", type=str)

    def handle(self, *args, **options):
        json_file = options["migration_json"]
        if not json_file:
            sys.stderr.write("please provide a migration json file name\n")
            exit(1)

        json_path = getattr(settings, "BK_IAM_MIGRATION_JSON_PATH", "support-files/iam/")
        file_path = os.path.join(settings.BASE_DIR, json_path, json_file)

        if not os.path.exists(file_path):
            sys.stderr.write("{} is not exist.\n".format(file_path))
            exit(1)

        loader = MigrationLoader(None, ignore_no_migrations=False)
        migration_leaf = loader.graph.leaf_nodes(IAMMigrationConfig.name)

        is_initial = True
        last_migration_name = None

        if migration_leaf:
            is_initial = False
            last_migration_name = migration_leaf[0][1]

        sys.stdout.write("is initial migration: {}\n".format(is_initial))
        sys.stdout.write("last migration: {}\n".format(last_migration_name))

        migration_name = self.migration_name(last_migration_name)
        migration_file = "{}.py".format(
            os.path.join(settings.BASE_DIR, "iam/contrib/iam_migration/migrations", migration_name,)
        )

        with codecs.open(migration_file, mode="w", encoding="utf-8") as fp:
            fp.write(
                render_to_string(
                    MIGRATION_TEMPLATE_NAME,
                    {
                        "migration_json": json_file,
                        "app_label": IAMMigrationConfig.name,
                        "initial": is_initial,
                        "last_migration_name": last_migration_name,
                    },
                )
            )

    def migration_name(self, last_migration_name):
        system_id = getattr(settings, "BK_IAM_SYSTEM_ID", None)
        time = datetime.now().strftime("%Y%m%d%H%M")

        if not system_id:
            self.stderr.write("You must set BK_IAM_SYSTEM_ID in django settings before make migrations")
            exit(1)

        if not last_migration_name:
            return "0001_initial"

        code = "%04d" % (int(last_migration_name[:4]) + 1)

        return "{code}_{system_id}_{time}".format(code=code, system_id=system_id, time=time)
