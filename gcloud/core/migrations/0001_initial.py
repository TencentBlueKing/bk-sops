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

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='Business',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cc_id', models.IntegerField(unique=True)),
                ('cc_name', models.CharField(max_length=100)),
                ('cc_owner', models.CharField(max_length=100)),
                ('cc_company', models.CharField(max_length=100)),
            ],
            options={
                'verbose_name': '\u4e1a\u52a1 Business',
                'verbose_name_plural': '\u4e1a\u52a1 Business',
                'permissions': (('view_business', 'Can view business'), ('manage_business', 'Can manage business')),
            },
        ),
        migrations.CreateModel(
            name='BusinessGroupMembership',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now)),
                ('business', models.ForeignKey(to='core.Business')),
                ('group', models.ForeignKey(to='auth.Group')),
            ],
            options={
                'verbose_name': '\u4e1a\u52a1\u7528\u6237\u7ec4 BusinessGroupMembership',
                'verbose_name_plural': '\u4e1a\u52a1\u7528\u6237\u7ec4 BusinessGroupMembership',
            },
        ),
        migrations.CreateModel(
            name='UserBusiness',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('user', models.CharField(unique=True, max_length=255, verbose_name='\u7528\u6237QQ')),
                ('default_buss', models.IntegerField(verbose_name='\u9ed8\u8ba4\u4e1a\u52a1')),
            ],
            options={
                'verbose_name': '\u7528\u6237\u9ed8\u8ba4\u4e1a\u52a1 UserBusiness',
                'verbose_name_plural': '\u7528\u6237\u9ed8\u8ba4\u4e1a\u52a1 UserBusiness',
            },
        ),
        migrations.AddField(
            model_name='business',
            name='groups',
            field=models.ManyToManyField(to='auth.Group', through='core.BusinessGroupMembership'),
        ),
        migrations.AlterUniqueTogether(
            name='businessgroupmembership',
            unique_together=set([('business', 'group')]),
        ),
    ]
