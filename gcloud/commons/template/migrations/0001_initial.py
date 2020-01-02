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
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('pipeline', '0013_old_template_process'),
    ]

    operations = [
        migrations.CreateModel(
            name='CommonTemplate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('category', models.CharField(default=b'Other', max_length=255, verbose_name='\u6a21\u677f\u7c7b\u578b', choices=[(b'OpsTools', '\u8fd0\u7ef4\u5de5\u5177'), (b'MonitorAlarm', '\u76d1\u63a7\u544a\u8b66'), (b'ConfManage', '\u914d\u7f6e\u7ba1\u7406'), (b'DevTools', '\u5f00\u53d1\u5de5\u5177'), (b'EnterpriseIT', '\u4f01\u4e1aIT'), (b'OfficeApp', '\u529e\u516c\u5e94\u7528'), (b'Other', '\u5176\u5b83')])),
                ('notify_type', models.CharField(default=b'[]', max_length=128, verbose_name='\u6d41\u7a0b\u4e8b\u4ef6\u901a\u77e5\u65b9\u5f0f')),
                ('notify_receivers', models.TextField(default=b'{}', verbose_name='\u6d41\u7a0b\u4e8b\u4ef6\u901a\u77e5\u4eba')),
                ('time_out', models.IntegerField(default=20, verbose_name='\u6d41\u7a0b\u8d85\u65f6\u65f6\u95f4(\u5206\u949f)')),
                ('is_deleted', models.BooleanField(default=False, verbose_name='\u662f\u5426\u5220\u9664')),
                ('collector', models.ManyToManyField(to=settings.AUTH_USER_MODEL, verbose_name='\u6536\u85cf\u6a21\u677f\u7684\u4eba', blank=True)),
                ('pipeline_template', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to_field=b'template_id', blank=True, to='pipeline.PipelineTemplate', null=True)),
            ],
            options={
                'ordering': ['-id'],
                'abstract': False,
                'verbose_name': '\u516c\u5171\u6d41\u7a0b\u6a21\u677f CommonTemplate',
                'verbose_name_plural': '\u516c\u5171\u6d41\u7a0b\u6a21\u677f CommonTemplate',
                'permissions': [('create_task', '\u65b0\u5efa\u4efb\u52a1'), ('fill_params', '\u586b\u5199\u53c2\u6570'), ('execute_task', '\u6267\u884c\u4efb\u52a1')],
            },
        ),
    ]
