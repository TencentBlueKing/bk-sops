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



from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_auto_20181130_1510'),
    ]

    operations = [
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256, verbose_name='\u9879\u76ee\u540d')),
                ('time_zone', models.CharField(blank=True, max_length=100, verbose_name='\u9879\u76ee\u65f6\u533a')),
                ('creator', models.CharField(max_length=256, verbose_name='\u521b\u5efa\u8005')),
                ('desc', models.CharField(max_length=512, verbose_name='\u9879\u76ee\u63cf\u8ff0')),
                ('create_at', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65f6\u95f4')),
                ('from_cmdb', models.BooleanField(default=False, verbose_name='\u662f\u5426\u662f\u4ece CMDB \u4e1a\u52a1\u540c\u6b65\u8fc7\u6765\u7684\u9879\u76ee')),
                ('cmdb_biz_id', models.IntegerField(default=-1, verbose_name='\u4e1a\u52a1\u540c\u6b65\u9879\u76ee\u5bf9\u5e94\u7684 CMDB \u4e1a\u52a1 ID')),
                ('is_disable', models.BooleanField(default=False, verbose_name='\u662f\u5426\u5df2\u505c\u7528')),
                ('relate_business', models.ManyToManyField(to='core.Business', verbose_name='\u5173\u8054\u9879\u76ee')),
            ],
        ),
        migrations.CreateModel(
            name='UserDefaultProject',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=255, unique=True, verbose_name='\u7528\u6237\u540d')),
                ('default_project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Project', verbose_name='\u7528\u6237\u9ed8\u8ba4\u9879\u76ee')),
            ],
        ),
    ]
