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

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('weixin_core', '0004_weixinusersession'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='weixinusersession',
            options={'verbose_name': '\u5fae\u4fe1\u7528\u6237Session\u8bb0\u5f55', 'verbose_name_plural': '\u5fae\u4fe1\u7528\u6237Session\u8bb0\u5f55'},
        ),
    ]
