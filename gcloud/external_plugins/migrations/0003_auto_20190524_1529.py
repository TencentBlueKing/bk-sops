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

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('external_plugins', '0002_cachepackagesource_desc'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='cachepackagesource',
            options={'ordering': ['-id'], 'verbose_name': '\u8fdc\u7a0b\u5305\u6e90\u7f13\u5b58 CachePackageSource', 'verbose_name_plural': '\u8fdc\u7a0b\u5305\u6e90\u7f13\u5b58 CachePackageSource'},
        ),
        migrations.AlterModelOptions(
            name='filesystemoriginalsource',
            options={'ordering': ['-id'], 'verbose_name': 'FS\u8fdc\u7a0b\u5305\u6e90 FileSystemOriginalSource', 'verbose_name_plural': 'FS\u8fdc\u7a0b\u5305\u6e90 FileSystemOriginalSource'},
        ),
        migrations.AlterModelOptions(
            name='gitrepooriginalsource',
            options={'ordering': ['-id'], 'verbose_name': 'GIT\u8fdc\u7a0b\u5305\u6e90 GitRepoOriginalSource', 'verbose_name_plural': 'GIT\u8fdc\u7a0b\u5305\u6e90 GitRepoOriginalSource'},
        ),
        migrations.AlterModelOptions(
            name='s3originalsource',
            options={'ordering': ['-id'], 'verbose_name': 'S3\u8fdc\u7a0b\u5305\u6e90 S3OriginalSource', 'verbose_name_plural': 'S3\u8fdc\u7a0b\u5305\u6e90 S3OriginalSource'},
        ),
    ]
