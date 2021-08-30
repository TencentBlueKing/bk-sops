# Generated by Django 2.2.16 on 2021-08-30 10:59

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="MigrateLog",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("templateInPipeline_start", models.IntegerField(verbose_name="template迁移起点")),
                ("componentInTemplate_start", models.IntegerField(verbose_name="componet迁移起点")),
                ("instanceInPipeline_start", models.IntegerField(verbose_name="instance迁移起点")),
                ("componentExecuteData_start", models.IntegerField(verbose_name="componentExecute迁移起点")),
                ("migrated", models.IntegerField(verbose_name="已迁移量")),
                ("finished", models.IntegerField(verbose_name="迁移任务是否正常结束")),
                ("templateInPipeline_end", models.IntegerField(verbose_name="template迁移终点")),
                ("componentInTemplate_end", models.IntegerField(verbose_name="component迁移终点")),
                ("instanceInPipeline_end", models.IntegerField(verbose_name="instance迁移终点")),
                ("componenetExecuteData_end", models.IntegerField(verbose_name="componentExecute迁移终点")),
            ],
        ),
    ]
