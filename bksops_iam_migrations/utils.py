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
import traceback

from django.db import connection


def finished_old_iam_migrations() -> set:
    with connection.cursor() as cursor:
        try:
            cursor.execute("SELECT name FROM django_migrations WHERE app = 'iam_migration'")
        except Exception:
            print("[finished_old_iam_migrations] fetch err", traceback.format_exc())
            return set()

        migration_names = cursor.fetchall()

    return {item[0] for item in migration_names}
