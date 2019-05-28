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

from django.db import migrations, models


def reverse_func(apps, schema_editor):
    TaskTemplate = apps.get_model('tasktmpl3', 'TaskTemplate')
    PipelineTemplate = apps.get_model('pipeline', 'PipelineTemplate')
    db_alias = schema_editor.connection.alias
    templates = TaskTemplate.objects.using(db_alias).all()
    for t in templates:
        t.pipeline_template_id = PipelineTemplate.objects.using(db_alias).get(id=t.tmp_field_id).id
        t.save()


def forward_func(apps, schema_editor):
    TaskTemplate = apps.get_model('tasktmpl3', 'TaskTemplate')
    PipelineTemplate = apps.get_model('pipeline', 'PipelineTemplate')
    db_alias = schema_editor.connection.alias
    templates = TaskTemplate.objects.using(db_alias).all()
    for t in templates:
        t.pipeline_template_id = PipelineTemplate.objects.using(db_alias).get(id=t.tmp_field_id).template_id
        t.save()


class Migration(migrations.Migration):
    dependencies = [
        ('tasktmpl3', '0008_auto_20180908_1453'),
    ]

    operations = [
        migrations.RunPython(forward_func, reverse_func)
    ]

