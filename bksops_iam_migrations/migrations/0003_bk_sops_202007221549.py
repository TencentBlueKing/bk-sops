# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import os
import json
import codecs

from django.db import migrations
from django.conf import settings

from iam.contrib.iam_migration.migrator import IAMMigrator

from bksops_iam_migrations.utils import finished_old_iam_migrations


def forward_func(apps, schema_editor):

    if "0003_bk_sops_202007221549" in finished_old_iam_migrations():
        print("0003_bk_sops_202007221549 already run at iam_migrations, skip.")
        return

    migrator = IAMMigrator(Migration.migration_json)
    migrator.migrate()


class Migration(migrations.Migration):
    migration_json = "03_add_related_actions.json"

    dependencies = [("bksops_iam_migrations", "0002_bk_sops_202007091136")]

    operations = [migrations.RunPython(forward_func)]
