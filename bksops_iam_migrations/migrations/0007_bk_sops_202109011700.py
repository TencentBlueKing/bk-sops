# -*- coding: utf-8 -*-

from django.db import migrations


class Migration(migrations.Migration):
    migration_json = "07_add_common_actions.json"

    dependencies = [("bksops_iam_migrations", "0006_bk_sops_202106171007")]

    operations = [migrations.RunPython(migrations.RunPython.noop)]
