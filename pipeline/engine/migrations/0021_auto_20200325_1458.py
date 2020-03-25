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
        ('engine', '0020_pipelinemodel_priority'),
    ]

    operations = [
        migrations.AlterField(
            model_name='functionswitch',
            name='description',
            field=models.TextField(default='', verbose_name='功能描述'),
        ),
        migrations.AlterField(
            model_name='history',
            name='data',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='engine.HistoryData'),
        ),
        migrations.AlterField(
            model_name='nodecelerytask',
            name='celery_task_id',
            field=models.CharField(default='', max_length=40, verbose_name='celery 任务 ID'),
        ),
        migrations.AlterField(
            model_name='pipelineprocess',
            name='current_node_id',
            field=models.CharField(db_index=True, default='', max_length=32, verbose_name='当前推进到的节点的 ID'),
        ),
        migrations.AlterField(
            model_name='pipelineprocess',
            name='destination_id',
            field=models.CharField(default='', max_length=32, verbose_name='遇到该 ID 的节点就停止推进'),
        ),
        migrations.AlterField(
            model_name='pipelineprocess',
            name='parent_id',
            field=models.CharField(default='', max_length=32, verbose_name='父 process 的 ID'),
        ),
        migrations.AlterField(
            model_name='pipelineprocess',
            name='snapshot',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='engine.ProcessSnapshot'),
        ),
        migrations.AlterField(
            model_name='processcelerytask',
            name='celery_task_id',
            field=models.CharField(default='', max_length=40, verbose_name='celery 任务 ID'),
        ),
        migrations.AlterField(
            model_name='schedulecelerytask',
            name='celery_task_id',
            field=models.CharField(default='', max_length=40, verbose_name='celery 任务 ID'),
        ),
        migrations.AlterField(
            model_name='status',
            name='name',
            field=models.CharField(default='', max_length=64, verbose_name='节点名称'),
        ),
    ]
