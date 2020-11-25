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



from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('taskflow3', '0010_auto_20190827_1943'),
    ]

    operations = [
        migrations.AlterField(
            model_name='taskflowinstance',
            name='template_id',
            field=models.CharField(blank=True, max_length=255, verbose_name='\u521b\u5efa\u4efb\u52a1\u6240\u7528\u7684\u6a21\u677fID'),
        ),
        migrations.AlterField(
            model_name='taskflowinstance',
            name='template_source',
            field=models.CharField(choices=[(b'project', '\u9879\u76ee\u6d41\u7a0b'), (b'common', '\u516c\u5171\u6d41\u7a0b'), (b'onetime', '\u4e00\u6b21\u6027\u4efb\u52a1')], default='project', max_length=32, verbose_name='\u6d41\u7a0b\u6a21\u677f\u6765\u6e90'),
        ),
    ]
