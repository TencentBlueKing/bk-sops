# Generated by Django 3.2.15 on 2023-12-05 06:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0025_auto_20230609_2101"),
    ]

    operations = [
        migrations.CreateModel(
            name="UserFavoriteProject",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("username", models.CharField(max_length=128, verbose_name="用户名")),
                ("project_id", models.IntegerField(verbose_name="项目id")),
            ],
            options={
                "verbose_name": "用户收藏项目 UserFavoriteProject",
                "verbose_name_plural": "用户收藏项目 UserFavoriteProject",
                "unique_together": {("username", "project_id")},
            },
        ),
    ]
