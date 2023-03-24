# -*- coding: utf-8 -*-

from django.db import migrations

from iam.contrib.iam_migration.migrator import IAMMigrator


def forward_func(apps, schema_editor):
    migrator = IAMMigrator(Migration.migration_json)
    migrator.migrate()


class Migration(migrations.Migration):
    migration_json = "15_update_biz_operator_actions.json"

    dependencies = [("bksops_iam_migrations", "0014_bk_sops_202209211105")]

    operations = [migrations.RunPython(forward_func)]
