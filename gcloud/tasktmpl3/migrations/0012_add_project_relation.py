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
    Project = apps.get_model('core', 'Project')
    db_alias = schema_editor.connection.alias

    projects = Project.objects.filter(from_cmdb=True)
    cc_id_to_project = {proj.cmdb_biz_id: proj for proj in projects}
    templates = TaskTemplate.objects.using(db_alias).all()

    template_count = len(templates)
    print('')
    for i, t in enumerate(templates, start=1):
        t.project = cc_id_to_project[t.business.cc_id]
        t.save()
        print("TaskTemplate project relationship build: (%s/%s)" % (i, template_count))


class Migration(migrations.Migration):
    dependencies = [
        ('tasktmpl3', '0011_tasktemplate_project'),
        ('core', '0010_create_project_for_exist_biz'),
    ]

    operations = [
        migrations.RunPython(forward_func, reverse_func)
    ]
