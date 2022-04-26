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

RUN_VER = os.getenv("RUN_VER", "open")

IS_PAAS_V3 = int(os.getenv("BKPAAS_MAJOR_VERSION", False)) == 3
IS_OPEN_V3 = IS_PAAS_V3 and RUN_VER == "open"

if IS_OPEN_V3:
    from env_v3 import *  # noqa
else:
    from env_v2 import *  # noqa

if not IS_OPEN_V3 and IS_PAAS_V3:
    BKPAAS_SERVICE_ADDRESSES_BKSAAS = os.getenv("BKPAAS_SERVICE_ADDRESSES_BKSAAS")
    SOPS_CALLBACK_MODULE_NAME = "callback"
    SOPS_API_SERVER_MODULE_NAME = "api"
    BK_SAAS_HOSTS_DICT = (
        json.loads(base64.b64decode(BKPAAS_SERVICE_ADDRESSES_BKSAAS).decode("utf-8"))
        if BKPAAS_SERVICE_ADDRESSES_BKSAAS
        else {}
    )
    BK_SAAS_HOSTS = {}
    for item in BK_SAAS_HOSTS_DICT:
        BK_SAAS_HOSTS.setdefault(item["key"]["bk_app_code"], {})
        BK_SAAS_HOSTS[item["key"]["bk_app_code"]][item["key"]["module_name"] or BKSAAS_DEFAULT_MODULE_NAME] = item[
            "value"
        ][os.getenv("BKPAAS_ENVIRONMENT", "prod")]

    # CALLBACK 回调地址
    BKAPP_INNER_CALLBACK_HOST = os.getenv(
        "BKAPP_INNER_CALLBACK_HOST", BK_SAAS_HOSTS[APP_CODE][SOPS_CALLBACK_MODULE_NAME] or BK_PAAS_INNER_HOST + SITE_URL
    )
    # API SERVER服务地址
    BKAPP_INNER_API_SERVER_HOST = os.getenv(
        "BKAPP_INNER_API_SERVER_HOST",
        BK_SAAS_HOSTS[APP_CODE][SOPS_API_SERVER_MODULE_NAME] or BK_PAAS_INNER_HOST + SITE_URL,
    )

    # APIGW 访问地址
    BK_APIGW_URL_TMPL = os.getenv("BK_API_URL_TMPL")

# 蓝鲸监控自定义上报配置
BK_MONITOR_REPORT_ENABLE = int(os.getenv("MONITOR_REPORT_ENABLE", 0)) == 1
BK_MONITOR_REPORT_URL = os.getenv("MONITOR_REPORT_URL")
BK_MONITOR_REPORT_DATA_ID = int(os.getenv("MONITOR_REPORT_DATA_ID", -1))
BK_MONITOR_REPORT_ACCESS_TOKEN = os.getenv("MONITOR_REPORT_ACCESS_TOKEN")
BK_MONITOR_REPORT_TARGET = os.getenv("MONITOR_REPORT_TARGET")
BK_MONITOR_REPORT_INTERVAL = int(os.getenv("MONITOR_REPORT_INTERVAL", 10))
BK_MONITOR_REPORT_CHUNK_SIZE = int(os.getenv("MONITOR_REPORT_CHUNK_SIZE", 200))

ENABLE_OTEL_TRACE = os.getenv("BKAPP_ENABLE_OTEL_TRACE", False)

BK_APP_OTEL_INSTRUMENT_DB_API = os.getenv("BKAPP_OTEL_INSTRUMENT_DB_API", False)

NODE_CALLBACK_RETRY_TIMES = int(os.getenv("NODE_CALLBACK_RETRY_TIMES", 3))

# 蓝鲸插件开发地址
BK_PLUGIN_DEVELOP_URL = os.getenv("BK_PLUGIN_DEVELOP_URL", "")

# 蓝鲸插件授权过滤 APP
PLUGIN_DISTRIBUTOR_NAME = os.getenv("PLUGIN_DISTRIBUTOR_NAME", None)

# 蓝鲸API网关
BK_IAM_APIGW_HOST = os.getenv("BK_IAM_APIGW_HOST")

# CALLBACK 回调入口，处理走网关回调的场景
BKAPP_INNER_CALLBACK_ENTRY = os.getenv("BKAPP_INNER_CALLBACK_ENTRY", "")

# 网关管理员
BK_APIGW_MANAGER_MAINTAINERS = os.getenv("BK_APIGW_MANAGER_MAINTAINERS", "admin").split(",")
