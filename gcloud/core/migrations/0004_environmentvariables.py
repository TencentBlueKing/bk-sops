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
        ('core', '0003_business_executor'),
    ]

    operations = [
        migrations.CreateModel(
            name='EnvironmentVariables',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key', models.CharField(unique=True, max_length=255, verbose_name='\u53d8\u91cfKEY')),
                ('name', models.CharField(max_length=255, verbose_name='\u53d8\u91cf\u63cf\u8ff0', blank=True)),
                ('value', models.CharField(max_length=1000, verbose_name='\u53d8\u91cf\u503c', blank=True)),
            ],
            options={
                'verbose_name': '\u73af\u5883\u53d8\u91cf EnvironmentVariables',
                'verbose_name_plural': '\u73af\u5883\u53d8\u91cf EnvironmentVariables',
            },
        ),
    ]
