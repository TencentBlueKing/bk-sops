# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""


from django.db import migrations


def reverse_func(apps, schema_editor):
    PeriodicTask = apps.get_model("periodictask", "PeriodicTask")
    db_alias = schema_editor.connection.alias
    PeriodicTask.objects.using(db_alias).all().update(creator="")


def forward_func(apps, schema_editor):
    PeriodicTask = apps.get_model("periodictask", "PeriodicTask")
    db_alias = schema_editor.connection.alias

    tasks = PeriodicTask.objects.using(db_alias).all()

    for t in tasks:
        t.creator = t.task.creator
        t.save()

    tasks.update(create_time=None, edit_time=None)


class Migration(migrations.Migration):
    dependencies = [
        ("periodictask", "0008_auto_20220520_2149"),
    ]

    operations = [migrations.RunPython(forward_func, reverse_func)]
