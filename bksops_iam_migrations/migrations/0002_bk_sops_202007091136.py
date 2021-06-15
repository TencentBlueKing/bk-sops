# -*- coding: utf-8 -*-

import os
import json
import codecs

from django.db import migrations
from django.conf import settings

from iam.contrib.iam_migration.migrator import IAMMigrator

from bksops_iam_migrations.utils import finished_old_iam_migrations


def forward_func(apps, schema_editor):

    if "0002_bk_sops_202007091136" in finished_old_iam_migrations():
        print("0002_bk_sops_202007091136 already run at iam_migrations, skip.")
        return

    migrator = IAMMigrator(Migration.migration_json)
    migrator.migrate()


class Migration(migrations.Migration):
    migration_json = "02_add_action_group.json"

    dependencies = [("bksops_iam_migrations", "0001_initial")]

    operations = [migrations.RunPython(forward_func)]
