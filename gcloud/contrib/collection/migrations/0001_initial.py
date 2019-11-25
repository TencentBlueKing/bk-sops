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

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Collection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=255, verbose_name='\u7528\u6237\u540d')),
                ('category', models.CharField(choices=[(b'process', '\u9879\u76ee\u6d41\u7a0b'), (b'common', '\u516c\u5171\u6d41\u7a0b'), (b'periodic', '\u5468\u671f\u4efb\u52a1'), (b'app_maker', '\u8f7b\u5e94\u7528')], max_length=255, verbose_name='\u6536\u85cf\u5bf9\u8c61\u7c7b\u578b')),
                ('extra_info', models.TextField(blank=True, verbose_name='\u989d\u5916\u4fe1\u606f')),
            ],
            options={
                'verbose_name': '\u7528\u6237\u6536\u85cf Collection',
                'verbose_name_plural': '\u7528\u6237\u6536\u85cf Collection',
            },
        ),
    ]
