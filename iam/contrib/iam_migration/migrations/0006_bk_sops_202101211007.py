# -*- coding: utf-8 -*-
import os
import json
import codecs

from django.db import migrations
from django.conf import settings

from iam.contrib.iam_migration.migrator import IAMMigrator


def forward_func(apps, schema_editor):

    migrator = IAMMigrator(Migration.migration_json)
    migrator.migrate()


class Migration(migrations.Migration):
    migration_json = "06_mini_app_create_task_relate_actions.json"

    dependencies = [("iam_migration", "0005_bk_sops_202012081507")]

    operations = [migrations.RunPython(forward_func)]
