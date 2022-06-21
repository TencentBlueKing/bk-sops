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

import os

RUN_VER = os.getenv("RUN_VER", "open")

IS_PAAS_V3 = int(os.getenv("BKPAAS_MAJOR_VERSION", False)) == 3
IS_OPEN_V3 = IS_PAAS_V3 and RUN_VER == "open"

if IS_OPEN_V3:
    from env_v3 import *  # noqa
else:
    from env_v2 import *  # noqa

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

NODE_CALLBACK_RETRY_TIMES = int(os.getenv("NODE_CALLBACK_RETRY_TIMES", os.getenv("BKAPP_NODE_CALLBACK_RETRY_TIMES", 5)))

# 蓝鲸插件开发地址
BK_PLUGIN_DEVELOP_URL = os.getenv("BK_PLUGIN_DEVELOP_URL", "")

# 蓝鲸插件授权过滤 APP
PLUGIN_DISTRIBUTOR_NAME = os.getenv("PLUGIN_DISTRIBUTOR_NAME", None)

# IAM APIGW 地址
BK_IAM_APIGW_HOST = os.getenv("BK_IAM_APIGW_HOST")

# 节点日志持久化时间
BK_NODE_LOG_PERSISTENT_DAYS = int(os.getenv("BKAPP_NODE_LOG_PERSISTENT_DAYS", 30))

# CALLBACK 回调入口，处理走网关回调的场景
BKAPP_INNER_CALLBACK_ENTRY = os.getenv("BKAPP_INNER_CALLBACK_ENTRY", "")

# 网关管理员
BK_APIGW_MANAGER_MAINTAINERS = os.getenv("BK_APIGW_MANAGER_MAINTAINERS", "admin").split(",")

# 启动节点日志数据源拉取
NODE_LOG_DATA_SOURCE = os.getenv("NODE_LOG_DATA_SOURCE", "DATABASE")
NODE_LOG_DATA_SOURCE_CONFIG = json.loads(os.getenv("NODE_LOG_DATA_SOURCE_CONFIG", "{}"))

# PAAS V3 APIGW token
PAASV3_APIGW_API_TOKEN = os.getenv("BKAPP_PAASV3_APIGW_API_TOKEN")

# APIGW 访问地址
BK_APIGW_URL_TMPL = os.getenv("BK_API_URL_TMPL")

# 是否允许 celery worker 发送监控事件
CELERY_SEND_EVENTS = bool(os.getenv("CELERY_SEND_EVENTS", False))
