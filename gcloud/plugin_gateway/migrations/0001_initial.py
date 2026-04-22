# -*- coding: utf-8 -*-

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="PluginGatewaySourceConfig",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("source_key", models.CharField(max_length=64, unique=True)),
                ("display_name", models.CharField(max_length=128)),
                ("default_project_id", models.BigIntegerField(blank=True, null=True)),
                ("callback_domain_allow_list", models.JSONField(default=list)),
                ("plugin_allow_list", models.JSONField(default=list)),
                ("is_enabled", models.BooleanField(default=True)),
                ("create_time", models.DateTimeField(auto_now_add=True)),
                ("update_time", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "插件网关来源配置",
                "verbose_name_plural": "插件网关来源配置",
                "ordering": ["source_key"],
            },
        ),
        migrations.CreateModel(
            name="PluginGatewayRun",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("source_key", models.CharField(db_index=True, max_length=64)),
                ("plugin_id", models.CharField(db_index=True, max_length=128)),
                ("plugin_version", models.CharField(max_length=64)),
                ("client_request_id", models.CharField(max_length=128)),
                ("open_plugin_run_id", models.CharField(db_index=True, max_length=64, unique=True)),
                ("callback_url", models.URLField(max_length=512)),
                ("callback_token", models.CharField(max_length=512)),
                ("run_status", models.CharField(db_index=True, max_length=32)),
                ("caller_app_code", models.CharField(db_index=True, max_length=64)),
                ("trigger_payload", models.JSONField(default=dict)),
                ("outputs", models.JSONField(default=dict)),
                ("error_message", models.TextField(blank=True, default="")),
                ("create_time", models.DateTimeField(auto_now_add=True)),
                ("update_time", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "插件网关执行记录",
                "verbose_name_plural": "插件网关执行记录",
                "ordering": ["-create_time", "-id"],
            },
        ),
        migrations.AddConstraint(
            model_name="plugingatewayrun",
            constraint=models.UniqueConstraint(
                fields=("caller_app_code", "client_request_id"),
                name="uniq_plugin_gateway_app_request",
            ),
        ),
    ]
