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
import timezone_field.fields


class Migration(migrations.Migration):

    dependencies = [
        ('periodic_task', '0002_auto_20190103_1918'),
    ]

    operations = [
        migrations.AlterField(
            model_name='crontabschedule',
            name='day_of_month',
            field=models.CharField(default='*', max_length=64, verbose_name='day of month'),
        ),
        migrations.AlterField(
            model_name='crontabschedule',
            name='day_of_week',
            field=models.CharField(default='*', max_length=64, verbose_name='day of week'),
        ),
        migrations.AlterField(
            model_name='crontabschedule',
            name='hour',
            field=models.CharField(default='*', max_length=64, verbose_name='hour'),
        ),
        migrations.AlterField(
            model_name='crontabschedule',
            name='minute',
            field=models.CharField(default='*', max_length=64, verbose_name='minute'),
        ),
        migrations.AlterField(
            model_name='crontabschedule',
            name='month_of_year',
            field=models.CharField(default='*', max_length=64, verbose_name='month of year'),
        ),
        migrations.AlterField(
            model_name='crontabschedule',
            name='timezone',
            field=timezone_field.fields.TimeZoneField(default='UTC'),
        ),
        migrations.AlterField(
            model_name='djceleryperiodictask',
            name='args',
            field=models.TextField(blank=True, default='[]', help_text='JSON encoded positional arguments', verbose_name='Arguments'),
        ),
        migrations.AlterField(
            model_name='djceleryperiodictask',
            name='kwargs',
            field=models.TextField(blank=True, default='{}', help_text='JSON encoded keyword arguments', verbose_name='Keyword arguments'),
        ),
        migrations.AlterField(
            model_name='intervalschedule',
            name='period',
            field=models.CharField(choices=[('days', 'Days'), ('hours', 'Hours'), ('minutes', 'Minutes'), ('seconds', 'Seconds'), ('microseconds', 'Microseconds')], max_length=24, verbose_name='period'),
        ),
        migrations.AlterField(
            model_name='periodictask',
            name='creator',
            field=models.CharField(default='', max_length=32, verbose_name='创建者'),
        ),
    ]
