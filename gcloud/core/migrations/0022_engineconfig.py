# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0021_auto_20210125_1943"),
    ]

    operations = [
        migrations.CreateModel(
            name="EngineConfig",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("scope_id", models.IntegerField(verbose_name="范围对象ID")),
                ("scope", models.IntegerField(choices=[(1, "project"), (2, "template")], verbose_name="配置范围")),
                ("engine_ver", models.IntegerField(choices=[(1, "v1"), (2, "v2")], verbose_name="引擎版本")),
                (
                    "template_source",
                    models.CharField(
                        choices=[("project", "项目流程"), ("common", "公共流程"), ("onetime", "一次性任务")],
                        max_length=32,
                        verbose_name="流程模板来源",
                    ),
                ),
            ],
            options={
                "verbose_name": "引擎版本配置 ProjectConfig",
                "verbose_name_plural": "引擎版本配置 ProjectConfig",
                "index_together": {("scope", "scope_id")},
            },
        ),
    ]
