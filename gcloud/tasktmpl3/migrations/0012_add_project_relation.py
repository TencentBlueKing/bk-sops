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

from __future__ import unicode_literals

from django.db import migrations


def reverse_func(apps, schema_editor):
    TaskTemplate = apps.get_model('tasktmpl3', 'TaskTemplate')
    db_alias = schema_editor.connection.alias
    TaskTemplate.objects.using(db_alias).all().update(project=None)


def forward_func(apps, schema_editor):
    TaskTemplate = apps.get_model('tasktmpl3', 'TaskTemplate')
    Business = apps.get_model('core', 'Business')

    cc_ids = Business.objects.all().values_list('cc_id', flat=True)

    for cc_id in cc_ids:
        TaskTemplate.objects.filter(business__cc_id=cc_id).update(project_id=cc_id)


class Migration(migrations.Migration):
    dependencies = [
        ('tasktmpl3', '0011_tasktemplate_project'),
        ('core', '0011_create_project_for_non_active_biz'),
    ]

    operations = [
        migrations.RunPython(forward_func, reverse_func)
    ]
