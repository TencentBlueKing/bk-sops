# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-

from django.db import migrations
from iam.contrib.iam_migration.migrator import IAMMigrator


def forward_func(apps, schema_editor):
    migrator = IAMMigrator(Migration.migration_json)
    migrator.migrate()


class Migration(migrations.Migration):
    migration_json = "16_add_publish_draft_actions.json"

    dependencies = [("bksops_iam_migrations", "0015_bk_sops_202212122120")]

    operations = [migrations.RunPython(forward_func)]
