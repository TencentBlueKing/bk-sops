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

    dependencies = [
        ('appmaker', '0003_auto_20180301_1729'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='appmaker',
            name='default_viewer',
        ),
        migrations.AlterField(
            model_name='appmaker',
            name='template_schema_id',
            field=models.CharField(max_length=100, verbose_name='\u6267\u884c\u65b9\u6848', blank=True),
        ),
    ]
