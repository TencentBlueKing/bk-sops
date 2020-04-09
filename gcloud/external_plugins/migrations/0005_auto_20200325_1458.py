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
        ('external_plugins', '0004_synctask'),
    ]

    operations = [
        migrations.AlterField(
            model_name='synctask',
            name='create_method',
            field=models.CharField(choices=[('manual', '手动触发'), ('auto', '部署自动触发')], default='manual', max_length=32, verbose_name='创建方式'),
        ),
        migrations.AlterField(
            model_name='synctask',
            name='status',
            field=models.CharField(choices=[('RUNNING', '执行中'), ('SUCCEEDED', '成功'), ('FAILED', '失败')], default='RUNNING', max_length=32, verbose_name='同步状态'),
        ),
    ]
