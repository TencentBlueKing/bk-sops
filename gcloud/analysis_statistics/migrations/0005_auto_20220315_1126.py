# Generated by Django 2.2.26 on 2022-03-15 03:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("analysis_statistics", "0004_merge_20211129_1011"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="taskflowexecutednodestatistics",
            options={"verbose_name": "Pipeline标准插件执行数据", "verbose_name_plural": "Pipeline标准插件执行数据"},
        ),
        migrations.CreateModel(
            name="TemplateVariableStatistics",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("template_id", models.BigIntegerField(verbose_name="模板 ID")),
                ("project_id", models.IntegerField(verbose_name="项目 ID, 公共流程的数据为 -1")),
                ("variable_key", models.CharField(max_length=256, verbose_name="变量键")),
                ("variable_type", models.CharField(db_index=True, max_length=256, verbose_name="变量类型")),
                ("variable_source", models.CharField(max_length=64, verbose_name="变量来源")),
                ("refs", models.IntegerField(verbose_name="被引用次数")),
            ],
            options={
                "unique_together": {("template_id", "project_id", "variable_key")},
            },
        ),
    ]
