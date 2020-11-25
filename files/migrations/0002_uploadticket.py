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
        ('files', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='UploadTicket',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=32, verbose_name='unique code')),
                ('applicant', models.CharField(max_length=128, verbose_name='which user apply this ticket')),
                ('apply_from', models.CharField(max_length=128, verbose_name='which ip apply this ticket')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='ticket create time')),
                ('is_available', models.BooleanField(verbose_name='wether this ticket is available')),
                ('used_at', models.DateTimeField(null=True, verbose_name='ticket use time')),
            ],
        ),
    ]
