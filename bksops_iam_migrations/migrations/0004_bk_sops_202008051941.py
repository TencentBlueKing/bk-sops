# -*- coding: utf-8 -*-

from django.db import migrations


class Migration(migrations.Migration):
    migration_json = "04_add_resource_creator_action.json"

    dependencies = [("bksops_iam_migrations", "0003_bk_sops_202007221549")]

    operations = [migrations.RunPython(migrations.RunPython.noop)]
