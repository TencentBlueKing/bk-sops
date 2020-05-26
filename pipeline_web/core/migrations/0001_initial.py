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

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='NodeInInstance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('node_id', models.CharField(max_length=32, verbose_name='节点ID')),
                ('node_type', models.CharField(max_length=100, verbose_name='节点类型')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('edit_time', models.DateTimeField(auto_now=True, verbose_name='修改时间')),
                ('instance_id', models.CharField(db_index=True, max_length=32, verbose_name='所属实例ID')),
            ],
            options={
                'verbose_name': '流程实例节点 NodeInInstance',
                'verbose_name_plural': '流程实例节点 NodeInInstance',
                'ordering': ['-id'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='NodeInTemplate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('node_id', models.CharField(max_length=32, verbose_name='节点ID')),
                ('node_type', models.CharField(max_length=100, verbose_name='节点类型')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('edit_time', models.DateTimeField(auto_now=True, verbose_name='修改时间')),
                ('template_id', models.CharField(db_index=True, max_length=32, verbose_name='所属模板ID')),
                ('version', models.CharField(max_length=32, verbose_name='所属模板版本')),
            ],
            options={
                'verbose_name': '流程模板节点 NodeInTemplate',
                'verbose_name_plural': '流程模板节点 NodeInTemplate',
                'ordering': ['-id'],
                'abstract': False,
            },
        ),
        migrations.AlterUniqueTogether(
            name='nodeintemplate',
            unique_together=set([('node_id', 'template_id', 'version')]),
        ),
        migrations.AlterIndexTogether(
            name='nodeintemplate',
            index_together=set([('template_id', 'version')]),
        ),
        migrations.AlterUniqueTogether(
            name='nodeininstance',
            unique_together=set([('node_id', 'instance_id')]),
        ),
    ]
