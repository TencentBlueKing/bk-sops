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

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Label',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(db_index=True, max_length=255, verbose_name='标签编码')),
                ('name', models.CharField(max_length=255, verbose_name='标签名称')),
            ],
            options={
                'verbose_name': '标签 Label',
                'verbose_name_plural': '标签 Label',
            },
        ),
        migrations.CreateModel(
            name='LabelGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(db_index=True, max_length=255, verbose_name='标签分组编码')),
                ('name', models.CharField(max_length=255, verbose_name='标签分组名称')),
            ],
            options={
                'verbose_name': '标签分组 LabelGroup',
                'verbose_name_plural': '标签分组 LabelGroup',
            },
        ),
        migrations.AddField(
            model_name='label',
            name='group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='label.LabelGroup'),
        ),
    ]
