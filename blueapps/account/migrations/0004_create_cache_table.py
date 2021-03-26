# -*- coding: utf-8 -*-

from django.core.management import call_command
from django.db import migrations


def create_cache_table(apps, schema_editor):
    """
    创建 cache table
    """
    call_command("createcachetable", "account_cache")


class Migration(migrations.Migration):

    dependencies = [
        ("account", "0003_verifyinfo"),
    ]

    operations = [migrations.RunPython(create_cache_table)]
