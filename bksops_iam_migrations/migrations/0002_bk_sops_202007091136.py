# -*- coding: utf-8 -*-

from django.db import migrations


class Migration(migrations.Migration):
    migration_json = "02_add_action_group.json"

    dependencies = [("bksops_iam_migrations", "0001_initial")]

    operations = [migrations.RunPython(migrations.RunPython.noop)]
