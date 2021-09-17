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

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="ProjectConstant",
            fields=[
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                ("project_id", models.BigIntegerField(verbose_name="项目 ID")),
                ("name", models.CharField(max_length=255, verbose_name="变量名")),
                ("key", models.CharField(max_length=255, verbose_name="变量唯一键")),
                ("value", models.TextField(verbose_name="变量值")),
                ("desc", models.TextField(verbose_name="变量描述")),
                ("create_by", models.CharField(max_length=255, verbose_name="创建人")),
                ("create_at", models.DateTimeField(auto_now_add=True, verbose_name="创建时间")),
                ("update_by", models.CharField(max_length=255, verbose_name="更新人")),
                ("update_at", models.DateTimeField(auto_now=True, verbose_name="更新时间")),
            ],
            options={"unique_together": {("project_id", "key")},},
        ),
    ]
