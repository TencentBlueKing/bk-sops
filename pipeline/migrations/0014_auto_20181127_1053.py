# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
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
        ("pipeline", "0013_old_template_process"),
    ]

    operations = [
        migrations.AlterField(
            model_name="pipelineinstance",
            name="name",
            field=models.CharField(
                default=b"default_instance", max_length=128, verbose_name="\u5b9e\u4f8b\u540d\u79f0"
            ),
        ),
        migrations.AlterField(
            model_name="pipelinetemplate",
            name="name",
            field=models.CharField(
                default=b"default_template", max_length=128, verbose_name="\u6a21\u677f\u540d\u79f0"
            ),
        ),
    ]
