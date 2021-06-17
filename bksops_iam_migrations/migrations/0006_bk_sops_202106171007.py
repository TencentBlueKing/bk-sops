# -*- coding: utf-8 -*-

import os
import json
import codecs

from django.db import migrations
from django.conf import settings

from iam.contrib.iam_migration.migrator import IAMMigrator

from bksops_iam_migrations.utils import finished_old_iam_migrations


def forward_func(apps, schema_editor):

    if "0006_bk_sops_202106171007" in finished_old_iam_migrations():
        print("0006_bk_sops_202106171007 already run at iam_migrations, skip.")
        return

    migrator = IAMMigrator(Migration.migration_json)
    migrator.migrate()


class Migration(migrations.Migration):
    migration_json = "06_add_common_actions.json"

    dependencies = [("bksops_iam_migrations", "0005_bk_sops_202012081507")]

    operations = [migrations.RunPython(forward_func)]
