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
import sys

from config import RUN_VER

if RUN_VER == "open":
    from blueapps.patch.settings_open_saas import *  # noqa
else:
    from blueapps.patch.settings_paas_services import *  # noqa

import env

# 正式环境
RUN_MODE = "PRODUCT"

BK_IAM_SYNC_TEMPLATES = True

BK_IAM_RESOURCE_API_HOST = env.BK_IAM_RESOURCE_API_HOST

CSRF_COOKIE_NAME = APP_CODE + "_csrftoken"

default.logging_addition_settings(LOGGING, environment="prod")

BK_APIGW_STAGE_NAME = "prod"


def get_default_database_config_dict(settings_module):
    if os.getenv("GCS_MYSQL_NAME") and os.getenv("MYSQL_NAME"):
        db_prefix = os.getenv("DB_PREFIX")
        if not db_prefix:
            sys.stderr.write(
                "Without DB_PREFIX environment variable while 'GCS_MYSQL_NAME' and 'MYSQL_NAME' are configured."
            )
            return {}
    elif os.getenv("GCS_MYSQL_NAME"):
        db_prefix = "GCS_MYSQL"
    elif os.getenv("MYSQL_NAME"):
        db_prefix = "MYSQL"
    else:
        if not settings_module.get("IS_LOCAL", False):
            # 对应非GCS_MYSQL或MYSQL开头的情况，需开发者自行配置
            sys.stderr.write("DB_PREFIX config is not 'GCS_MYSQL' or 'MYSQL_NAME'\n")
        return {}
    return {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.environ["%s_NAME" % db_prefix],
        "USER": os.environ["%s_USER" % db_prefix],
        "PASSWORD": os.environ["%s_PASSWORD" % db_prefix],
        "HOST": os.getenv("SOPS_HOST") or os.environ["%s_HOST" % db_prefix],
        "PORT": os.environ["%s_PORT" % db_prefix],
        "OPTIONS": {"isolation_level": "repeatable read"},
    }


DATABASES = {"default": get_default_database_config_dict(locals())}
