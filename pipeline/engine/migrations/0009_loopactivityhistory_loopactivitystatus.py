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
        ('engine', '0008_schedulecelerytask'),
    ]

    operations = [
        migrations.CreateModel(
            name='LoopActivityHistory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('identifier', models.CharField(max_length=32, verbose_name='\u8282\u70b9 id', db_index=True)),
                ('loop', models.PositiveIntegerField(verbose_name='\u672c\u6b21\u5faa\u73af\u8ba1\u6570')),
                ('started_time', models.DateTimeField(verbose_name='\u5f00\u59cb\u65f6\u95f4')),
                ('archived_time', models.DateTimeField(verbose_name='\u7ed3\u675f\u65f6\u95f4')),
                ('state', models.CharField(max_length=10, verbose_name='\u6267\u884c\u72b6\u6001')),
                ('data', models.ForeignKey(to='engine.HistoryData')),
            ],
        ),
        migrations.CreateModel(
            name='LoopActivityStatus',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('identifier', models.CharField(max_length=32, verbose_name='\u8282\u70b9 id', db_index=True)),
                ('current_loop', models.PositiveIntegerField(verbose_name='\u672c\u6b21\u5faa\u73af\u6b21\u6570')),
                ('actual_loop', models.PositiveIntegerField(verbose_name='\u5b9e\u9645\u5faa\u73af\u6b21\u6570')),
                ('loop_times', models.PositiveIntegerField(verbose_name='\u6240\u9700\u5faa\u73af\u6b21\u6570')),
            ],
        ),
    ]
