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
        ('weixin_core', '0003_auto_20190531_1205'),
    ]

    operations = [
        migrations.CreateModel(
            name='WeixinUserSession',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bk_user_id', models.CharField(max_length=128, unique=True, verbose_name='[\u4f01\u4e1a]\u5fae\u4fe1\u7528\u6237\u552f\u4e00\u6807\u8bc6(\u516c\u4f17\u53f7openid/\u4f01\u4e1a\u5fae\u4fe1userid)')),
                ('session_key', models.CharField(max_length=32, unique=True, verbose_name='\u6709\u6548\u7684session key')),
                ('expired_time', models.DateTimeField(verbose_name='\u8fc7\u671f\u65f6\u95f4')),
            ],
        ),
    ]
