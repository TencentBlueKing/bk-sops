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

    dependencies = [
        ("taskflow3", "0013_auto_20210125_1943"),
    ]

    operations = [
        migrations.CreateModel(
            name="TaskOperationTimesConfig",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("project_id", models.IntegerField(verbose_name="项目 ID")),
                (
                    "operation",
                    models.CharField(
                        choices=[("start", "启动"), ("pause", "暂停"), ("resume", "恢复"), ("revoke", "撤销")],
                        max_length=64,
                        verbose_name="任务操作",
                    ),
                ),
                ("times", models.IntegerField(verbose_name="限制操作次数")),
                (
                    "time_unit",
                    models.CharField(
                        choices=[("m", "分钟"), ("h", "小时"), ("d", "天")], max_length=10, verbose_name="限制时间单位"
                    ),
                ),
            ],
            options={
                "verbose_name": "任务操作次数限制配置 TaskOperationTimesConfig",
                "verbose_name_plural": "任务操作次数限制配置 TaskOperationTimesConfig",
            },
        ),
        migrations.AlterUniqueTogether(
            name="taskoperationtimesconfig", unique_together=set([("project_id", "operation")]),
        ),
    ]
