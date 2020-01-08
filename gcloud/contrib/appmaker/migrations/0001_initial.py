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
        ('taskflow3', '0001_initial'),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AppMaker',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name='APP\u540d\u79f0')),
                ('code', models.CharField(max_length=255, verbose_name='APP\u7f16\u7801')),
                ('info', models.CharField(max_length=255, null=True, verbose_name='APP\u57fa\u672c\u4fe1\u606f', blank=True)),
                ('desc', models.CharField(max_length=255, null=True, verbose_name='APP\u63cf\u8ff0\u4fe1\u606f', blank=True)),
                ('logo_url', models.TextField(default=b'', verbose_name='\u8f7b\u5e94\u7528logo\u5b58\u653e\u5730\u5740', blank=True)),
                ('link', models.URLField(max_length=255, verbose_name='gcloud\u94fe\u63a5')),
                ('creator', models.CharField(max_length=100, verbose_name='\u521b\u5efa\u4eba')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65f6\u95f4')),
                ('editor', models.CharField(max_length=100, null=True, verbose_name='\u7f16\u8f91\u4eba', blank=True)),
                ('default_viewer', models.TextField(default=b'{}', verbose_name='\u53ef\u89c1\u8303\u56f4')),
                ('is_deleted', models.BooleanField(default=False, verbose_name='\u662f\u5426\u5220\u9664')),
                ('business', models.ForeignKey(verbose_name='\u6240\u5c5e\u4e1a\u52a1', to='core.Business')),
                ('task_flow', models.ForeignKey(verbose_name='\u5173\u8054\u4efb\u52a1', to='taskflow3.TaskFlowInstance')),
            ],
            options={
                'ordering': ['-id'],
                'verbose_name': '\u3010APP:App_maker\u3011App_maker',
                'verbose_name_plural': '\u3010APP:App_maker\u3011App_maker',
            },
        ),
    ]
