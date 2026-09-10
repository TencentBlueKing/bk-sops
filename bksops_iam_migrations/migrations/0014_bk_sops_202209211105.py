# -*- coding: utf-8 -*-

from django.db import migrations


class Migration(migrations.Migration):
    migration_json = "14_add_biz_read_actions.json"

    dependencies = [("bksops_iam_migrations", "0013_bk_sops_202203010917")]

    operations = [migrations.RunPython(migrations.RunPython.noop)]
