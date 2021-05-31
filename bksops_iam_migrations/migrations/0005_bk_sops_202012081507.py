# -*- coding: utf-8 -*-

import os
import json
import codecs

from django.db import migrations
from django.conf import settings

from iam.contrib.iam_migration.migrator import IAMMigrator

from bksops_iam_migrations.utils import finished_old_iam_migrations


def forward_func(apps, schema_editor):

    if "0005_bk_sops_202012081507" in finished_old_iam_migrations():
        print("0005_bk_sops_202012081507 already run at iam_migrations, skip.")
        return

    migrator = IAMMigrator(Migration.migration_json)
    migrator.migrate()


class Migration(migrations.Migration):
    migration_json = "05_add_common_actions.json"

    dependencies = [("bksops_iam_migrations", "0004_bk_sops_202008051941")]

    operations = [migrations.RunPython(forward_func)]
