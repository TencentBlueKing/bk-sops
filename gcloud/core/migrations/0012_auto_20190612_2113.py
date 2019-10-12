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


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_create_project_for_non_active_biz'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='project',
            options={'verbose_name': '\u9879\u76ee Project', 'verbose_name_plural': '\u9879\u76ee Project'},
        ),
        migrations.AlterModelOptions(
            name='userdefaultproject',
            options={'verbose_name': '\u7528\u6237\u9ed8\u8ba4\u9879\u76ee UserDefaultProject', 'verbose_name_plural': '\u7528\u6237\u9ed8\u8ba4\u9879\u76ee UserDefaultProject'},
        ),
        migrations.RenameField(
            model_name='project',
            old_name='cmdb_biz_id',
            new_name='bk_biz_id',
        ),
        migrations.AlterField(
            model_name='project',
            name='desc',
            field=models.CharField(blank=True, max_length=512, verbose_name='\u9879\u76ee\u63cf\u8ff0'),
        ),
        migrations.AlterField(
            model_name='project',
            name='relate_business',
            field=models.ManyToManyField(blank=True, to='core.Business', verbose_name='\u5173\u8054\u9879\u76ee'),
        ),
    ]
