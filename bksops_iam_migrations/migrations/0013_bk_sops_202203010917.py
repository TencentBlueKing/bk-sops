# -*- coding: utf-8 -*-

from django.db import migrations

from iam.contrib.iam_migration.migrator import IAMMigrator


def forward_func(apps, schema_editor):
    migrator = IAMMigrator(Migration.migration_json)
    migrator.migrate()


class Migration(migrations.Migration):
    migration_json = "13_update_common_flow_create_task_relate_actions.json"

    dependencies = [("iam.contrib.iam_migration", "0012_bk_sops_202111251154")]

    operations = [migrations.RunPython(forward_func)]
