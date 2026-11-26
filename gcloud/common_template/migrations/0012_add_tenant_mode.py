# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('template', '0011_merge_20260319_1717'),
    ]

    operations = [
        migrations.AddField(
            model_name='commontemplate',
            name='tenant_mode',
            field=models.CharField(
                choices=[('single', '单租户'), ('global', '全租户')],
                default='single',
                help_text='single: 单租户（仅本租户可见）; global: 全租户（所有租户可见）',
                max_length=16,
                verbose_name='租户模式',
                db_index=True
            ),
        ),
        migrations.AddIndex(
            model_name='commontemplate',
            index=models.Index(
                fields=['tenant_mode', 'tenant_id', 'is_deleted'],
                name='idx_common_tpl_tenant'
            ),
        ),
    ]
