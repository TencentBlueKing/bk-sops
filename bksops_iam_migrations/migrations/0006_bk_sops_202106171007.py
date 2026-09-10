# -*- coding: utf-8 -*-

from django.db import migrations


class Migration(migrations.Migration):
    migration_json = "06_add_common_actions.json"

    dependencies = [("bksops_iam_migrations", "0005_bk_sops_202012081507")]

    operations = [migrations.RunPython(migrations.RunPython.noop)]
