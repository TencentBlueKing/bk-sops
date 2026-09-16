# -*- coding: utf-8 -*-

from django.db import migrations


class Migration(migrations.Migration):
    migration_json = "05_add_common_actions.json"

    dependencies = [("bksops_iam_migrations", "0004_bk_sops_202008051941")]

    operations = [migrations.RunPython(migrations.RunPython.noop)]
