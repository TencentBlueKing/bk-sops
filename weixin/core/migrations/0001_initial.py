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
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BkWeixinUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('openid', models.CharField(unique=True, max_length=128, verbose_name='\u5fae\u4fe1\u7528\u6237\u5e94\u7528\u552f\u4e00\u6807\u8bc6')),
                ('nickname', models.CharField(max_length=127, verbose_name='\u6635\u79f0', blank=True)),
                ('gender', models.CharField(max_length=15, verbose_name='\u6027\u522b', blank=True)),
                ('country', models.CharField(max_length=63, verbose_name='\u56fd\u5bb6', blank=True)),
                ('province', models.CharField(max_length=63, verbose_name='\u7701\u4efd', blank=True)),
                ('city', models.CharField(max_length=63, verbose_name='\u57ce\u5e02', blank=True)),
                ('avatar_url', models.CharField(max_length=255, verbose_name='\u5934\u50cf', blank=True)),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='\u52a0\u5165\u65f6\u95f4')),
            ],
            options={
                'db_table': 'bk_weixin_user',
                'verbose_name': '\u5fae\u4fe1\u7528\u6237',
                'verbose_name_plural': '\u5fae\u4fe1\u7528\u6237',
            },
        ),
    ]
