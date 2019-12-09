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
from django.db import migrations
from django.conf import settings


def load_data(apps, schema_editor):
    """
    添加用户为管理员
    """
    User = apps.get_model("account", "User")
    for name in settings.INIT_SUPERUSER:
        User.objects.update_or_create(
            username=name,
            defaults={'is_staff': True, 'is_active': True, 'is_superuser': True}
        )


class Migration(migrations.Migration):
    dependencies = [
        # 分别修改为django app名及最后一个migration文件名
        # 例如：('home_application', '0001_initial')
        ('core', '0012_auto_20190612_2113'),
    ]
    operations = [
        migrations.RunPython(load_data)
    ]
