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


import os
import sys
import json
import codecs

from django.conf import settings

from iam.contrib.iam_migration.utils import do_migrate
from iam.contrib.iam_migration import exceptions


def upsert_system_render(data):
    resource_api_host = getattr(settings, "BK_IAM_RESOURCE_API_HOST", None)
    if resource_api_host:
        data["provider_config"]["host"] = resource_api_host


renders = {"upsert_system": upsert_system_render}


class IAMMigrator(object):
    def __init__(self, migration_json):
        self.migration_json = migration_json

    def migrate(self):
        iam_host = settings.BK_IAM_INNER_HOST
        app_code = settings.APP_CODE
        app_secret = settings.SECRET_KEY

        # only trigger migrator at db migrate
        if "migrate" not in sys.argv:
            return

        json_path = getattr(settings, "BK_IAM_MIGRATION_JSON_PATH", "support-files/iam/")
        file_path = os.path.join(settings.BASE_DIR, json_path, self.migration_json)

        with codecs.open(file_path, mode="r", encoding="utf-8") as fp:
            data = json.load(fp=fp)

        # data pre render
        for op in data["operations"]:
            if op["operation"] in renders:
                renders[op["operation"]](op["data"])

        ok, _ = do_migrate.api_ping(iam_host)
        if not ok:
            raise exceptions.NetworkUnreachableError("bk iam ping error")

        ok = do_migrate.do_migrate(data, iam_host, app_code, app_secret)
        if not ok:
            raise exceptions.MigrationFailError("iam migrate fail")
