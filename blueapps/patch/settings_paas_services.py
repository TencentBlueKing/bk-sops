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

import os

from config import default

from blueapps.conf import get_settings_from_module

locals().update(get_settings_from_module(default))

INSTALLED_APPS = locals()["INSTALLED_APPS"]
REMOTE_STATIC_URL = locals()["REMOTE_STATIC_URL"]

if not REMOTE_STATIC_URL.endswith("/"):
    REMOTE_STATIC_URL = "%s/" % REMOTE_STATIC_URL

# saas访问统计js 路径
REMOTE_ANALYSIS_URL = "%sanalysis.js" % REMOTE_STATIC_URL

# paas提供的前端api.js 路径
REMOTE_API_URL = "%sbk_api/api.js" % REMOTE_STATIC_URL

# 从 apigw jwt 中获取 app_code 的 键
APIGW_APP_CODE_KEY = "app_code"

# 从 apigw jwt 中获取 username 的 键
APIGW_USER_USERNAME_KEY = "username"

# sentry support

SENTRY_DSN = os.environ.get("SENTRY_DSN")
if SENTRY_DSN:
    INSTALLED_APPS += ("raven.contrib.django.raven_compat",)
    RAVEN_CONFIG = {
        "dsn": SENTRY_DSN,
    }

# apm support
APM_ID = os.environ.get("APM_ID")
APM_TOKEN = os.environ.get("APM_TOKEN")
if APM_ID and APM_TOKEN:
    INSTALLED_APPS += ("ddtrace.contrib.django",)
    DATADOG_TRACE = {
        "TAGS": {
            "env": os.getenv("BKPAAS_ENVIRONMENT", "dev"),
            "apm_id": APM_ID,
            "apm_token": APM_TOKEN,
        },
    }
    # requests for APIGateway/ESB
    # remove pymysql while Django Defaultdb has been traced already
    try:
        import requests  # noqa  # pylint: disable=unused-import
        from ddtrace import patch

        patch(requests=True, pymysql=False)
    except Exception as err:  # pylint: disable=broad-except
        print("patch fail for requests and pymysql: %s" % err)

# 非open环境使用页面的语言切换按钮来控制语言
IS_DISPLAY_LANGUAGE_CHANGE = "block"
