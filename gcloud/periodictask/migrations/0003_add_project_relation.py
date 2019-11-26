# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""



from django.db import migrations


def reverse_func(apps, schema_editor):
    PeriodicTask = apps.get_model('periodictask', 'PeriodicTask')
    db_alias = schema_editor.connection.alias
    PeriodicTask.objects.using(db_alias).all().update(project=None)


def forward_func(apps, schema_editor):
    PeriodicTask = apps.get_model('periodictask', 'PeriodicTask')
    db_alias = schema_editor.connection.alias

    tasks = PeriodicTask.objects.using(db_alias).all()

    for i, t in enumerate(tasks, start=1):
        t.project_id = t.business.cc_id
        t.task.extra_info['project_id'] = t.project_id  # add project_id to extra_info
        t.task.save()
        t.save()


class Migration(migrations.Migration):
    dependencies = [
        ('periodictask', '0002_periodictask_project'),
        ('core', '0011_create_project_for_non_active_biz'),
    ]

    operations = [
        migrations.RunPython(forward_func, reverse_func)
    ]
