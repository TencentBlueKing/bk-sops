# -*- coding: utf-8 -*-

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("plugin_gateway", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="plugingatewayrun",
            name="callback_token",
            field=models.TextField(),
        ),
        migrations.AddField(
            model_name="plugingatewayrun",
            name="callback_delivered_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
