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
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pipeline', '0023_set_is_revoked'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pipelineinstance',
            name='execution_snapshot',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='execution_snapshot_instances', to='pipeline.Snapshot', verbose_name='用于实例执行的结构数据'),
        ),
        migrations.AlterField(
            model_name='pipelineinstance',
            name='name',
            field=models.CharField(default='default_instance', max_length=128, verbose_name='实例名称'),
        ),
        migrations.AlterField(
            model_name='pipelineinstance',
            name='snapshot',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='snapshot_instances', to='pipeline.Snapshot', verbose_name='实例结构数据，指向实例对应的模板的结构数据'),
        ),
        migrations.AlterField(
            model_name='pipelineinstance',
            name='tree_info',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tree_info_instances', to='pipeline.TreeInfo', verbose_name='提前计算好的一些流程结构数据'),
        ),
        migrations.AlterField(
            model_name='pipelinetemplate',
            name='name',
            field=models.CharField(default='default_template', max_length=128, verbose_name='模板名称'),
        ),
        migrations.AlterField(
            model_name='templateversion',
            name='md5',
            field=models.CharField(db_index=True, max_length=32, verbose_name='快照字符串的md5'),
        ),
    ]
