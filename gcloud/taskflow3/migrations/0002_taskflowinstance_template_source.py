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
        ('taskflow3', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='taskflowinstance',
            name='template_source',
            field=models.CharField(default=b'business', max_length=32, verbose_name='\u6d41\u7a0b\u6a21\u677f\u6765\u6e90', choices=[(b'business', '\u4e1a\u52a1\u6d41\u7a0b'), (b'common', '\u516c\u5171\u6d41\u7a0b')]),
        ),
    ]
