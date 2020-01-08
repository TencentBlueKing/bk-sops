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
        ('external_plugins', '0003_auto_20190524_1529'),
    ]

    operations = [
        migrations.CreateModel(
            name='SyncTask',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('creator', models.CharField(blank=True, max_length=32, verbose_name='\u6267\u884c\u8005')),
                ('create_method', models.CharField(choices=[(b'manual', '\u624b\u52a8\u89e6\u53d1'), (b'auto', '\u90e8\u7f72\u81ea\u52a8\u89e6\u53d1')], default=b'manual', max_length=32, verbose_name='\u521b\u5efa\u65b9\u5f0f')),
                ('start_time', models.DateTimeField(auto_now_add=True, verbose_name='\u542f\u52a8\u65f6\u95f4')),
                ('finish_time', models.DateTimeField(blank=True, null=True, verbose_name='\u7ed3\u675f\u65f6\u95f4')),
                ('status', models.CharField(choices=[(b'RUNNING', '\u6267\u884c\u4e2d'), (b'SUCCEEDED', '\u6210\u529f'), (b'FAILED', '\u5931\u8d25')], default=b'RUNNING', max_length=32, verbose_name='\u540c\u6b65\u72b6\u6001')),
                ('details', models.TextField(blank=True, verbose_name='\u540c\u6b65\u8be6\u60c5\u4fe1\u606f')),
            ],
            options={
                'ordering': ['-id'],
                'verbose_name': '\u8fdc\u7a0b\u5305\u6e90\u540c\u6b65\u4efb\u52a1 SyncTask',
                'verbose_name_plural': '\u8fdc\u7a0b\u5305\u6e90\u540c\u6b65\u4efb\u52a1 SyncTask',
            },
        ),
    ]
