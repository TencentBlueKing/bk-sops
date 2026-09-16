# -*- coding: utf-8 -*-

from django.db import migrations


class Migration(migrations.Migration):
    migration_json = "09_update_action_group.json"

    dependencies = [("bksops_iam_migrations", "0008_bk_sops_202109261155")]

    operations = [migrations.RunPython(migrations.RunPython.noop)]
