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
    TaskFlowInstance = apps.get_model('taskflow3', 'TaskFlowInstance')
    db_alias = schema_editor.connection.alias
    TaskFlowInstance.objects.using(db_alias).all().update(project=None)


def forward_func(apps, schema_editor):
    TaskFlowInstance = apps.get_model('taskflow3', 'TaskFlowInstance')
    Project = apps.get_model('core', 'Project')
    db_alias = schema_editor.connection.alias

    projects = Project.objects.filter(from_cmdb=True)
    cc_id_to_project = {proj.cmdb_biz_id: proj for proj in projects}
    instances = TaskFlowInstance.objects.using(db_alias).all()

    instance_count = len(instances)
    print('')
    for i, instance in enumerate(instances, start=1):
        instance.project = cc_id_to_project[instance.business.cc_id]
        if instance.template_source == 'business':
            instance.template_source = 'project'
        instance.save()
        print("TaskFlowInstance project relationship build: (%s/%s)" % (i, instance_count))


class Migration(migrations.Migration):
    dependencies = [
        ('taskflow3', '0006_auto_20190523_1509'),
        ('core', '0010_create_project_for_exist_biz'),
    ]

    operations = [
        migrations.RunPython(forward_func, reverse_func)
    ]
