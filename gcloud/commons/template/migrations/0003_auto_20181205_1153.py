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
        ('template', '0002_auto_20181204_1813'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='commontemplate',
            options={'ordering': ['-id'], 'verbose_name': '\u516c\u5171\u6d41\u7a0b\u6a21\u677f CommonTemplate', 'verbose_name_plural': '\u516c\u5171\u6d41\u7a0b\u6a21\u677f CommonTemplate'},
        ),
        migrations.AlterModelOptions(
            name='commontmplperm',
            options={'verbose_name': '\u516c\u5171\u6d41\u7a0b\u6a21\u677f\u6743\u9650 CommonTmplPerm', 'verbose_name_plural': '\u516c\u5171\u6d41\u7a0b\u6a21\u677f\u6743\u9650 CommonTmplPerm', 'permissions': [('common_create_task', 'common template create task'), ('common_fill_params', 'common template fill params'), ('common_execute_task', 'common template execute task')]},
        ),
    ]
