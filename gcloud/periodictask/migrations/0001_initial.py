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
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('taskflow3', '0003_auto_20181214_1453'),
        ('core', '0006_business_always_use_executor'),
        ('periodic_task', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PeriodicTask',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('template_id', models.CharField(max_length=255, verbose_name='\u521b\u5efa\u4efb\u52a1\u6240\u7528\u7684\u6a21\u677fID')),
                ('business', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, verbose_name='\u4e1a\u52a1', blank=True, to='core.Business', null=True)),
                ('task', models.ForeignKey(verbose_name='pipeline \u5c42\u5468\u671f\u4efb\u52a1', to='periodic_task.PeriodicTask')),
            ],
            options={
                'ordering': ['-id'],
                'verbose_name': '\u5468\u671f\u4efb\u52a1 PeriodicTask',
                'verbose_name_plural': '\u5468\u671f\u4efb\u52a1 PeriodicTask',
            },
        ),
        migrations.CreateModel(
            name='PeriodicTaskHistory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ex_data', models.TextField(verbose_name='\u5f02\u5e38\u4fe1\u606f')),
                ('start_at', models.DateTimeField(verbose_name='\u5f00\u59cb\u65f6\u95f4')),
                ('start_success', models.BooleanField(default=True, verbose_name='\u662f\u5426\u542f\u52a8\u6210\u529f')),
                ('flow_instance', models.ForeignKey(verbose_name='\u6d41\u7a0b\u5b9e\u4f8b', to='taskflow3.TaskFlowInstance', null=True)),
                ('history', models.ForeignKey(verbose_name='pipeline \u5c42\u5468\u671f\u4efb\u52a1\u5386\u53f2', to='periodic_task.PeriodicTaskHistory')),
                ('task', models.ForeignKey(verbose_name='\u5468\u671f\u4efb\u52a1', to='periodictask.PeriodicTask')),
            ],
        ),
    ]
