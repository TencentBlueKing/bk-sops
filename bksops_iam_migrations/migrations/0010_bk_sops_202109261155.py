# -*- coding: utf-8 -*-

from django.db import migrations


class Migration(migrations.Migration):
    migration_json = "10_update_resource_creator_actions.json"

    dependencies = [("bksops_iam_migrations", "0009_bk_sops_202109261155")]

    operations = [migrations.RunPython(migrations.RunPython.noop)]
