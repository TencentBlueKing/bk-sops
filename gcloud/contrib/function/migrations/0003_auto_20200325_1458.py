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
        ('function', '0002_auto_20180413_1804'),
    ]

    operations = [
        migrations.AlterField(
            model_name='functiontask',
            name='status',
            field=models.CharField(choices=[('submitted', '未认领'), ('claimed', '已认领'), ('rejected', '已驳回'), ('executed', '已执行'), ('finished', '已完成')], default='submitted', max_length=32, verbose_name='单据状态'),
        ),
    ]
