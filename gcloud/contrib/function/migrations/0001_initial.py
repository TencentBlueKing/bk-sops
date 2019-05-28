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


class Migration(migrations.Migration):

    dependencies = [
        ('taskflow3', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='FunctionTask',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('creator', models.CharField(max_length=32, verbose_name='\u63d0\u5355\u4eba')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='\u63d0\u5355\u65f6\u95f4')),
                ('claimant', models.CharField(max_length=32, verbose_name='\u8ba4\u9886\u4eba', blank=True)),
                ('claim_time', models.DateTimeField(null=True, verbose_name='\u8ba4\u9886\u65f6\u95f4', blank=True)),
                ('rejecter', models.CharField(max_length=32, verbose_name='\u9a73\u56de\u4eba', blank=True)),
                ('reject_time', models.DateTimeField(null=True, verbose_name='\u9a73\u56de\u65f6\u95f4', blank=True)),
                ('predecessor', models.CharField(max_length=32, verbose_name='\u8f6c\u5355\u4eba', blank=True)),
                ('transfer_time', models.DateTimeField(null=True, verbose_name='\u8f6c\u5355\u65f6\u95f4', blank=True)),
                ('status', models.CharField(default=b'submitted', max_length=32, verbose_name='\u5355\u636e\u72b6\u6001', choices=[(b'submitted', '\u672a\u8ba4\u9886'), (b'claimed', '\u5df2\u8ba4\u9886'), (b'rejected', '\u5df2\u9a73\u56de'), (b'executed', '\u5df2\u6267\u884c'), (b'finished', '\u5df2\u5b8c\u6210')])),
                ('task', models.ForeignKey(related_name='function_task', to='taskflow3.TaskFlowInstance', help_text='\u804c\u80fd\u5316\u5355')),
            ],
            options={
                'ordering': ['-id'],
                'verbose_name': '\u804c\u80fd\u5316\u8ba4\u9886\u5355',
                'verbose_name_plural': '\u804c\u80fd\u5316\u8ba4\u9886\u5355',
            },
        ),
    ]
