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
        ('taskflow3', '0011_auto_20190906_1119'),
    ]

    operations = [
        migrations.AlterField(
            model_name='taskflowinstance',
            name='category',
            field=models.CharField(choices=[('OpsTools', '运维工具'), ('MonitorAlarm', '监控告警'), ('ConfManage', '配置管理'), ('DevTools', '开发工具'), ('EnterpriseIT', '企业IT'), ('OfficeApp', '办公应用'), ('Other', '其它')], default='Other', max_length=255, verbose_name='任务类型，继承自模板'),
        ),
        migrations.AlterField(
            model_name='taskflowinstance',
            name='create_method',
            field=models.CharField(choices=[('app', '手动'), ('api', 'API网关'), ('app_maker', '轻应用'), ('periodic', '周期任务'), ('mobile', '移动端')], default='app', max_length=30, verbose_name='创建方式'),
        ),
        migrations.AlterField(
            model_name='taskflowinstance',
            name='flow_type',
            field=models.CharField(choices=[('common', '默认任务流程'), ('common_func', '职能化任务流程')], default='common', max_length=255, verbose_name='任务流程类型'),
        ),
        migrations.AlterField(
            model_name='taskflowinstance',
            name='template_source',
            field=models.CharField(choices=[('project', '项目流程'), ('common', '公共流程'), ('onetime', '一次性任务')], default='project', max_length=32, verbose_name='流程模板来源'),
        ),
    ]
