# -*- coding: utf-8 -*-

from django.db import migrations

from iam.contrib.iam_migration.migrator import IAMMigrator


def forward_func(apps, schema_editor):
    migrator = IAMMigrator(Migration.migration_json)
    migrator.migrate()


class Migration(migrations.Migration):
    migration_json = "14_add_biz_read_actions.json"

    dependencies = [("bksops_iam_migrations", "0013_bk_sops_202203010917")]

    operations = [migrations.RunPython(forward_func)]
