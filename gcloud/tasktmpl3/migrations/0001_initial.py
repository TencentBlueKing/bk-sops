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
        ('core', '0002_business_time_zone'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('pipeline', '0002_auto_20180109_1825'),
    ]

    operations = [
        migrations.CreateModel(
            name='TaskTemplate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('category', models.CharField(default=b'Other', max_length=255, verbose_name='\u6a21\u677f\u7c7b\u578b', choices=[(b'OpsTools', '\u8fd0\u7ef4\u5de5\u5177'), (b'MonitorAlarm', '\u76d1\u63a7\u544a\u8b66'), (b'ConfManage', '\u914d\u7f6e\u7ba1\u7406'), (b'DevTools', '\u5f00\u53d1\u5de5\u5177'), (b'EnterpriseIT', '\u4f01\u4e1aIT'), (b'OfficeApp', '\u529e\u516c\u5e94\u7528'), (b'Other', '\u5176\u5b83')])),
                ('notify_type', models.CharField(default=b'[]', max_length=128, verbose_name='\u6d41\u7a0b\u4e8b\u4ef6\u901a\u77e5\u65b9\u5f0f')),
                ('notify_receivers', models.TextField(default=b'{}', verbose_name='\u6d41\u7a0b\u4e8b\u4ef6\u901a\u77e5\u4eba')),
                ('time_out', models.IntegerField(default=20, verbose_name='\u6d41\u7a0b\u8d85\u65f6\u65f6\u95f4(\u5206\u949f)')),
                ('is_deleted', models.BooleanField(default=False, verbose_name='\u662f\u5426\u5220\u9664')),
                ('business', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, verbose_name='\u6240\u5c5e\u4e1a\u52a1', blank=True, to='core.Business', null=True)),
                ('collector', models.ManyToManyField(to=settings.AUTH_USER_MODEL, verbose_name='\u6536\u85cf\u6a21\u677f\u7684\u4eba', blank=True)),
                ('pipeline_template', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='pipeline.PipelineTemplate', null=True)),
            ],
            options={
                'ordering': ['-id'],
                'verbose_name': '\u6d41\u7a0b\u6a21\u677f',
                'verbose_name_plural': '\u6d41\u7a0b\u6a21\u677f',
                'permissions': [('common_select_steps', '\u6b65\u9aa4\u9009\u62e9'), ('common_fill_params', '\u53c2\u6570\u586b\u5199'), ('common_execute_task', '\u4efb\u52a1\u6267\u884c'), ('common_finished', '\u5b8c\u6210'), ('common_func_select_steps', '\u6b65\u9aa4\u9009\u62e9'), ('common_func_func_submit', '\u63d0\u4ea4\u9700\u6c42'), ('common_func_func_claim', '\u804c\u80fd\u5316\u8ba4\u9886'), ('common_func_execute_task', '\u4efb\u52a1\u6267\u884c'), ('common_func_finished', '\u5b8c\u6210')],
            },
        ),
    ]
