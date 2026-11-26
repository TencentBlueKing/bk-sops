# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import traceback

from django.db import connection
from data_migration.conf import settings


def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [dict(list(zip(columns, row))) for row in cursor.fetchall()]


def old_uer_table_exist():
    """检查旧的用户表是否存在，兼容不同数据库"""
    old_table = getattr(settings, "USER_TABLE", "account_bkuser")

    # 使用 Django 的连接对象获取数据库类型
    db_vendor = connection.vendor

    with connection.cursor() as cursor:
        try:
            if db_vendor == 'mysql':
                # MySQL 使用 SHOW TABLES
                cursor.execute("SHOW TABLES;")
                rows = {item[0] for item in cursor.fetchall()}
            elif db_vendor == 'sqlite':
                # SQLite 使用 sqlite_master 系统表
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                rows = {item[0] for item in cursor.fetchall()}
            elif db_vendor == 'postgresql':
                # PostgreSQL 使用 information_schema
                cursor.execute("SELECT tablename FROM pg_tables WHERE schemaname='public';")
                rows = {item[0] for item in cursor.fetchall()}
            else:
                # 其他数据库，尝试使用 Django 的 introspection
                rows = set(connection.introspection.table_names(cursor))
        except Exception:
            print("old_uer_table_exist show tables error:", traceback.format_exc())
            return False

        return old_table in rows
