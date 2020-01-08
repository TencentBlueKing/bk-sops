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
import pipeline.engine.models


class Migration(migrations.Migration):

    dependencies = [
        ('engine', '0011_auto_20180830_1205'),
    ]

    operations = [
        migrations.CreateModel(
            name='LoopActivityScheduleHistory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('schedule_id', models.CharField(max_length=64, verbose_name='ID \u8282\u70b9ID+version')),
                ('activity_id', models.CharField(max_length=32, verbose_name='\u8282\u70b9 ID', db_index=True)),
                ('schedule_times', models.IntegerField(default=0, verbose_name='\u88ab\u8c03\u5ea6\u6b21\u6570')),
                ('wait_callback', models.BooleanField(default=False, verbose_name='\u662f\u5426\u662f\u56de\u8c03\u578b\u8c03\u5ea6')),
                ('callback_data', pipeline.engine.models.IOField(default=None, verbose_name='\u56de\u8c03\u6570\u636e')),
                ('version', models.CharField(max_length=32, verbose_name='Activity \u7684\u7248\u672c', db_index=True)),
                ('current_loop', models.PositiveIntegerField(verbose_name='\u5f53\u524d\u8c03\u5ea6\u6240\u5904\u7684\u5faa\u73af\u8ba1\u6570')),
            ],
        ),
        migrations.AddField(
            model_name='loopactivityhistory',
            name='schedule',
            field=models.ForeignKey(to='engine.LoopActivityScheduleHistory', null=True),
        ),
    ]
