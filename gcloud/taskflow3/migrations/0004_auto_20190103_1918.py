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
        ('taskflow3', '0003_auto_20181214_1453'),
    ]

    operations = [
        migrations.AlterField(
            model_name='taskflowinstance',
            name='create_method',
            field=models.CharField(default=b'app', max_length=30, verbose_name='\u521b\u5efa\u65b9\u5f0f', choices=[(b'app', '\u624b\u52a8'), (b'api', 'API\u7f51\u5173'), (b'app_maker', '\u8f7b\u5e94\u7528'), (b'periodic', '\u5468\u671f\u4efb\u52a1')]),
        ),
    ]
