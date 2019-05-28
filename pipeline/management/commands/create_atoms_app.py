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

import os

from django.core.management import call_command, base


class Command(base.BaseCommand):
    help = 'Create an application for atoms development'

    def add_arguments(self, parser):
        parser.add_argument('app_name', nargs=1, type=str)

    def handle(self, *args, **options):
        app_name = options['app_name'][0]
        if os.path.isdir(app_name):
            print 'the directory [%s] already exists, please try another name.'
            return
        call_command('startapp', app_name)

        collection_path = '%s/components/collections' % app_name
        static_collection_path = '%s/static/%s' % (app_name, app_name)
        init_file_path = [
            '%s/components/collections/__init__.py' % app_name,
            '%s/components/__init__.py' % app_name,
            '%s/components/collections/atom.py' % app_name,
            '%s/static/%s/atom.js' % (app_name, app_name),
        ]
        useless_file_path = [
            '%s/admin.py' % app_name,
            '%s/models.py' % app_name,
            '%s/tests.py' % app_name,
            '%s/views.py' % app_name
        ]
        os.makedirs(collection_path)
        os.makedirs(static_collection_path)
        for p in init_file_path:
            open(p, 'w+').close()
        for p in useless_file_path:
            os.remove(p)
