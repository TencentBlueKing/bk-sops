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

from config import default, get_env_or_raise

from blueapps.conf import get_settings_from_module
from blueapps.patch.log import get_paas_v2_logging_config_dict

locals().update(get_settings_from_module(default))

BK_URL = locals()["BK_URL"]
MIDDLEWARE = locals()["MIDDLEWARE"]
INSTALLED_APPS = locals()["INSTALLED_APPS"]
STATIC_URL = locals()["STATIC_URL"]
RUN_VER = locals()["RUN_VER"]

# ESB component
ESB_SDK_NAME = "blueking.component"

# 从 apigw jwt 中获取 app_code 的 键
APIGW_APP_CODE_KEY = "bk_app_code"

# 从 apigw jwt 中获取 username 的 键
APIGW_USER_USERNAME_KEY = "bk_username"

# PAASV2对外版不需要bkoauth,DISABLED_APPS加入bkoauth
INSTALLED_APPS = (
    INSTALLED_APPS[0 : INSTALLED_APPS.index("bkoauth")]
    + INSTALLED_APPS[INSTALLED_APPS.index("bkoauth") + 1 :]
)

# REMOTE_STATIC_URL
REMOTE_STATIC_URL = "%sremote/" % STATIC_URL

# 请求官方 API 默认版本号，可选值为："v2" 或 ""；其中，"v2"表示规范化API，
# ""表示未规范化API.如果外面设置了该值则使用设置值,否则默认使用v2
DEFAULT_BK_API_VER = locals().get("DEFAULT_BK_API_VER", "v2")

# open环境使用cookie中的blueking_language来控制语言
LANGUAGE_SESSION_KEY = "blueking_language"
LANGUAGE_COOKIE_NAME = "blueking_language"
IS_DISPLAY_LANGUAGE_CHANGE = "none"

# CSRF Config
CSRF_COOKIE_NAME = "csrftoken"

IS_OPEN_V3 = os.getenv("BKPAAS_MAJOR_VERSION", False)


# 判断open环境对应的PaaS版本
def is_open_saas_v2():
    return RUN_VER == "open" and not IS_OPEN_V3


if is_open_saas_v2():  # V2
    # 蓝鲸PASS平台URL
    BK_PAAS_HOST = os.getenv("BK_PAAS_HOST", BK_URL).rstrip("/")

    # 用于 用户认证、用户信息获取 的蓝鲸主机
    BK_PAAS_INNER_HOST = os.getenv("BK_PAAS_INNER_HOST", BK_PAAS_HOST).rstrip("/")

    # 兼容component的APP_ID,APP_TOKEN
    APP_CODE = APP_ID = get_env_or_raise("APP_ID")
    SECRET_KEY = APP_TOKEN = get_env_or_raise("APP_TOKEN")

    # IS_LOCAL,V2和V3的判断方式不同,V2用BK_ENV
    IS_LOCAL = not os.getenv("BK_ENV", False)

    # 日志
    BK_LOG_DIR = os.getenv("BK_LOG_DIR", "/data/apps/logs/")
    LOGGING = get_paas_v2_logging_config_dict(
        is_local=IS_LOCAL,
        bk_log_dir=BK_LOG_DIR,
        log_level=locals().get("LOG_LEVEL", "INFO"),
    )

    # PAASV2对外版不需要whitenoise,MIDDLEWARE中去除'whitenoise.middleware.WhiteNoiseMiddleware'
    MIDDLEWARE = (
        MIDDLEWARE[0 : MIDDLEWARE.index("whitenoise.middleware.WhiteNoiseMiddleware")]
        + MIDDLEWARE[MIDDLEWARE.index("whitenoise.middleware.WhiteNoiseMiddleware") + 1 :]
    )

    # BROKER_URL
    if "BK_BROKER_URL" in os.environ:
        BROKER_URL = os.getenv("BK_BROKER_URL")

    # SITE_URL,STATIC_URL,,FORCE_SCRIPT_NAME
    # 测试环境
    if os.getenv("BK_ENV") == "testing":
        BK_URL = os.environ.get("BK_URL", "%s/console/" % BK_PAAS_HOST)
        SITE_URL = os.environ.get("BK_SITE_URL", "/t/%s/" % APP_CODE)
        STATIC_URL = "%sstatic/" % SITE_URL
    # 正式环境
    if os.getenv("BK_ENV") == "production":
        BK_URL = os.environ.get("BK_URL", "%s/console/" % BK_PAAS_HOST)
        SITE_URL = os.environ.get("BK_SITE_URL", "/o/%s/" % APP_CODE)
        STATIC_URL = "%sstatic/" % SITE_URL

    # STATIC_ROOT,静态文件收集文件夹,由于企业版需要用户手动收集,此处设为空,
    # 同时需要设置STATICFILES_DIRS不改变
    STATIC_ROOT = None

    # saas访问统计js 路径
    REMOTE_ANALYSIS_URL = "%s/console/static/js/analysis.min.js" % BK_PAAS_HOST

    # paas提供的前端api.js 路径
    REMOTE_API_URL = "%s/console/static/bk_api/api.js" % BK_PAAS_HOST

    # 蓝鲸开发者页面
    BK_DEV_URL = "%s/app/list/" % BK_PAAS_HOST

    # 蓝鲸登陆页面
    BK_LOGIN_URL = BK_PAAS_HOST + "/login"
    BK_LOGIN_INNER_URL = BK_PAAS_INNER_HOST + "/login"

else:  # V3
    # 蓝鲸PASS平台URL
    BK_PAAS_HOST = os.getenv("BK_PAAS2_URL", BK_URL).rstrip("/")

    # 用于 用户认证、用户信息获取 的蓝鲸主机
    BK_PAAS_INNER_HOST = os.getenv("BK_PAAS2_INNER_URL", BK_PAAS_HOST).rstrip("/")

    # 兼容component的APP_ID,APP_TOKEN
    APP_CODE = APP_ID = get_env_or_raise("BKPAAS_APP_ID")
    SECRET_KEY = APP_TOKEN = get_env_or_raise("BKPAAS_APP_SECRET")

    # 蓝鲸登陆页面
    BK_LOGIN_URL = os.getenv("BK_LOGIN_URL", "%s/login" % BK_PAAS_HOST).rstrip("/")
    BK_LOGIN_INNER_URL = os.getenv("BK_LOGIN_INNER_URL", "%s/login" % BK_PAAS_INNER_HOST).rstrip("/")
