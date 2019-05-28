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
        ('core', '0002_business_time_zone'),
        ('pipeline', '0002_auto_20180109_1825'),
    ]

    operations = [
        migrations.CreateModel(
            name='TaskFlowInstance',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('category', models.CharField(default=b'Other', max_length=255, verbose_name='\u4efb\u52a1\u7c7b\u578b\uff0c\u7ee7\u627f\u81ea\u6a21\u677f', choices=[(b'OpsTools', '\u8fd0\u7ef4\u5de5\u5177'), (b'MonitorAlarm', '\u76d1\u63a7\u544a\u8b66'), (b'ConfManage', '\u914d\u7f6e\u7ba1\u7406'), (b'DevTools', '\u5f00\u53d1\u5de5\u5177'), (b'EnterpriseIT', '\u4f01\u4e1aIT'), (b'OfficeApp', '\u529e\u516c\u5e94\u7528'), (b'Other', '\u5176\u5b83')])),
                ('template_id', models.CharField(max_length=255, verbose_name='\u521b\u5efa\u4efb\u52a1\u6240\u7528\u7684\u6a21\u677fID')),
                ('create_method', models.CharField(default=b'app', max_length=30, verbose_name='\u521b\u5efa\u65b9\u5f0f', choices=[(b'app', 'APP'), (b'api', 'API'), (b'app_maker', 'App_maker')])),
                ('create_info', models.CharField(max_length=255, verbose_name='\u521b\u5efa\u4efb\u52a1\u989d\u5916\u4fe1\u606f\uff08App maker ID\u6216\u8005APP CODE\uff09', blank=True)),
                ('flow_type', models.CharField(default=b'common', max_length=255, verbose_name='\u4efb\u52a1\u6d41\u7a0b\u7c7b\u578b', choices=[(b'common', '\u9ed8\u8ba4\u4efb\u52a1\u6d41\u7a0b'), (b'common_func', '\u804c\u80fd\u5316\u4efb\u52a1\u6d41\u7a0b')])),
                ('current_flow', models.CharField(max_length=255, verbose_name='\u5f53\u524d\u4efb\u52a1\u6d41\u7a0b\u9636\u6bb5')),
                ('is_deleted', models.BooleanField(default=False, verbose_name='\u662f\u5426\u5220\u9664')),
                ('business', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, verbose_name='\u4e1a\u52a1', blank=True, to='core.Business', null=True)),
                ('pipeline_instance', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='pipeline.PipelineInstance', null=True)),
            ],
            options={
                'ordering': ['-id'],
                'verbose_name': '\u6d41\u7a0b\u5b9e\u4f8b TaskFlowInstance',
                'verbose_name_plural': '\u6d41\u7a0b\u5b9e\u4f8b TaskFlowInstance',
            },
        ),
    ]
