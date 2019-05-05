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

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='GitRepoSyncSource',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128, verbose_name='\u540c\u6b65\u6e90\u540d')),
                ('repo_address', models.TextField(verbose_name='\u4ed3\u5e93\u94fe\u63a5')),
                ('branch', models.CharField(max_length=128, verbose_name='\u5206\u652f\u540d')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MainPackageSource',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(max_length=64, verbose_name='\u5305\u6e90\u7c7b\u578b')),
                ('base_source_id', models.IntegerField(verbose_name='\u5305\u6e90\u6a21\u578b ID')),
            ],
        ),
        migrations.CreateModel(
            name='RootPackage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128, verbose_name='\u5305\u540d')),
                ('source_type', models.CharField(max_length=64, verbose_name='\u5305\u6e90\u7c7b\u578b')),
                ('source_id', models.IntegerField(verbose_name='\u540c\u6b65\u6e90 ID')),
            ],
        ),
    ]
