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
        ('template', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CommonTmplPerm',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('common_template_id', models.CharField(max_length=255, verbose_name='\u901a\u7528\u6d41\u7a0b\u6a21\u677fID')),
                ('biz_cc_id', models.CharField(max_length=255, verbose_name='\u901a\u7528\u6d41\u7a0b\u6a21\u677fID')),
            ],
            options={
                'permissions': [('create_task', '\u65b0\u5efa\u4efb\u52a1'), ('fill_params', '\u586b\u5199\u53c2\u6570'), ('execute_task', '\u6267\u884c\u4efb\u52a1')],
                'verbose_name': '\u516c\u5171\u6d41\u7a0b\u6a21\u677f\u6743\u9650 CommonTmplPerm',
                'verbose_name_plural': '\u516c\u5171\u6d41\u7a0b\u6a21\u677f\u6743\u9650 CommonTmplPerm',
            },
        ),
        migrations.AlterUniqueTogether(
            name='commontmplperm',
            unique_together=set([('common_template_id', 'biz_cc_id')]),
        ),
        migrations.AlterIndexTogether(
            name='commontmplperm',
            index_together=set([('common_template_id', 'biz_cc_id')]),
        ),
    ]
