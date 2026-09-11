# -*- coding: utf-8 -*-

from django.db import migrations


class Migration(migrations.Migration):
    migration_json = "08_add_clocked_task_actions.json"

    dependencies = [("bksops_iam_migrations", "0007_bk_sops_202109011700")]

    operations = [migrations.RunPython(migrations.RunPython.noop)]
