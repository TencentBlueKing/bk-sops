# -*- coding: utf-8 -*-

from django.db import migrations

from iam.contrib.iam_migration.migrator import IAMMigrator


def forward_func(apps, schema_editor):
    migrator = IAMMigrator(Migration.migration_json)
    migrator.migrate()


class Migration(migrations.Migration):
    migration_json = "17_update_action_group.json"

    dependencies = [("bksops_iam_migrations", "0016_bk_sops_202212291113")]

    operations = [migrations.RunPython(forward_func)]
