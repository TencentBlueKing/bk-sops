# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="DeprecatedPlugin",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("code", models.CharField(max_length=255, verbose_name="插件编码")),
                ("version", models.CharField(max_length=64, verbose_name="插件版本")),
                ("type", models.PositiveIntegerField(choices=[(1, "component"), (2, "variable")], verbose_name="插件类型")),
                (
                    "phase",
                    models.PositiveIntegerField(
                        choices=[(1, "will be deprecated"), (2, "deprecated")], verbose_name="生命周期"
                    ),
                ),
            ],
        ),
    ]
