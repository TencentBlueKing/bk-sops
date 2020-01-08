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
import pipeline.contrib.external_plugins.models.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CachePackageSource',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(max_length=64, verbose_name='\u5305\u6e90\u7c7b\u578b')),
                ('base_source_id', models.IntegerField(blank=True, null=True, verbose_name='\u5305\u6e90\u6a21\u578b ID')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='FileSystemOriginalSource',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(max_length=64, verbose_name='\u5305\u6e90\u7c7b\u578b')),
                ('base_source_id', models.IntegerField(blank=True, null=True, verbose_name='\u5305\u6e90\u6a21\u578b ID')),
                ('name', models.CharField(max_length=128, verbose_name='\u5305\u6e90')),
                ('desc', models.TextField(blank=True, max_length=1000, verbose_name='\u5305\u6e90\u8bf4\u660e')),
                ('packages', pipeline.contrib.external_plugins.models.fields.JSONTextField(verbose_name='\u6a21\u5757\u914d\u7f6e')),
                ('path', models.TextField(verbose_name='\u6587\u4ef6\u7cfb\u7edf\u8def\u5f84')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='GitRepoOriginalSource',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(max_length=64, verbose_name='\u5305\u6e90\u7c7b\u578b')),
                ('base_source_id', models.IntegerField(blank=True, null=True, verbose_name='\u5305\u6e90\u6a21\u578b ID')),
                ('name', models.CharField(max_length=128, verbose_name='\u5305\u6e90')),
                ('desc', models.TextField(blank=True, max_length=1000, verbose_name='\u5305\u6e90\u8bf4\u660e')),
                ('packages', pipeline.contrib.external_plugins.models.fields.JSONTextField(verbose_name='\u6a21\u5757\u914d\u7f6e')),
                ('repo_address', models.TextField(verbose_name='\u4ed3\u5e93\u94fe\u63a5')),
                ('repo_raw_address', models.TextField(help_text='\u53ef\u4ee5\u901a\u8fc7web\u76f4\u63a5\u8bbf\u95ee\u6e90\u6587\u4ef6\u7684\u94fe\u63a5\u524d\u7f00', verbose_name='\u6587\u4ef6\u6258\u7ba1\u4ed3\u5e93\u94fe\u63a5')),
                ('branch', models.CharField(max_length=128, verbose_name='\u5206\u652f\u540d')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='S3OriginalSource',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(max_length=64, verbose_name='\u5305\u6e90\u7c7b\u578b')),
                ('base_source_id', models.IntegerField(blank=True, null=True, verbose_name='\u5305\u6e90\u6a21\u578b ID')),
                ('name', models.CharField(max_length=128, verbose_name='\u5305\u6e90')),
                ('desc', models.TextField(blank=True, max_length=1000, verbose_name='\u5305\u6e90\u8bf4\u660e')),
                ('packages', pipeline.contrib.external_plugins.models.fields.JSONTextField(verbose_name='\u6a21\u5757\u914d\u7f6e')),
                ('service_address', models.TextField(verbose_name='\u5bf9\u8c61\u5b58\u50a8\u670d\u52a1\u5730\u5740')),
                ('bucket', models.TextField(verbose_name='bucket \u540d')),
                ('access_key', models.TextField(verbose_name='access key')),
                ('secret_key', models.TextField(verbose_name='secret key')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
