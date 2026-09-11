# -*- coding: utf-8 -*-

from django.db import migrations


class Migration(migrations.Migration):
    migration_json = "01_initial.json"

    dependencies = []

    # Historical IAM V3 SDK migration. IAM V4 model registration starts at 0016.
    operations = [migrations.RunPython(migrations.RunPython.noop)]
