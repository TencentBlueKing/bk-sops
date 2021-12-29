# -*- coding: utf-8 -*-

from django.db import migrations

from iam.contrib.iam_migration.migrator import IAMMigrator


def forward_func(apps, schema_editor):
    migrator = IAMMigrator(Migration.migration_json)
    migrator.migrate()


class Migration(migrations.Migration):
    migration_json = "12_update_mini_app_related_actions.json"

    dependencies = [("bksops_iam_migrations", "0011_bk_sops_202109261155")]

    operations = [migrations.RunPython(forward_func)]
