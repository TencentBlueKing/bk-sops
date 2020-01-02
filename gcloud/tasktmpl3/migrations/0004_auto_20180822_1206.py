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
        ('tasktmpl3', '0003_auto_20180301_1732'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='tasktemplate',
            options={'ordering': ['-id'], 'verbose_name': '\u6d41\u7a0b\u6a21\u677f TaskTemplate', 'verbose_name_plural': '\u6d41\u7a0b\u6a21\u677f TaskTemplate', 'permissions': [('create_task', '\u65b0\u5efa\u4efb\u52a1'), ('fill_params', '\u586b\u5199\u53c2\u6570'), ('execute_task', '\u6267\u884c\u4efb\u52a1')]},
        ),
    ]
