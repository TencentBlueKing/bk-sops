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
import datetime

from django.db import connection
from django.apps import AppConfig


class DataMigrationConfig(AppConfig):
    name = 'data_migration'

    def ready(self):
        try:
            import djcelery
        except Exception:
            return

        # djcelery upgrate compatible
        if djcelery.__version__.split('.')[1] >= 2:
            with connection.cursor() as cursor:
                cursor.execute('show tables;')
                tables = {item[0] for item in cursor.fetchall()}
                is_first_migrate = 'django_migrations' not in tables
                if is_first_migrate:
                    return

                using_djcelery = 'djcelery_taskstate' in tables
                if not using_djcelery:
                    return

                # insert djcelery migration record
                cursor.execute('select * from `django_migrations` where app=\'djcelery\' and name=\'0001_initial\';')
                row = cursor.fetchall()
                if not row:
                    cursor.execute('insert into `django_migrations` (app, name, applied) '
                                   'values (\'djcelery\', \'0001_initial\', \'%s\');' %
                                   datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
