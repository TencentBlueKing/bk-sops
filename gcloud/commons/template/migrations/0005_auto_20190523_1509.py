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



from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('template', '0004_set_min_template_id'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='commontmplperm',
            options={'verbose_name': '\u516c\u5171\u6d41\u7a0b\u6a21\u677f\u6743\u9650 CommonTmplPerm', 'verbose_name_plural': '\u516c\u5171\u6d41\u7a0b\u6a21\u677f\u6743\u9650 CommonTmplPerm'},
        ),
    ]
