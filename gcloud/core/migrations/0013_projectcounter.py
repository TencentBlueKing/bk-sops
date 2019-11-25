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
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_auto_20190612_2113'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProjectCounter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=255, verbose_name='\u7528\u6237\u540d')),
                ('count', models.IntegerField(default=1, verbose_name='\u9879\u76ee\u8bbf\u95ee\u6b21\u6570')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Project', verbose_name='\u7528\u6237\u9ed8\u8ba4\u9879\u76ee')),
            ],
            options={
                'verbose_name': '\u7528\u6237\u8bbf\u95ee\u9879\u76ee\u8ba1\u6570 ProjectCounter',
                'verbose_name_plural': '\u7528\u6237\u8bbf\u95ee\u9879\u76ee\u8ba1\u6570 ProjectCounter',
            },
        ),
    ]
