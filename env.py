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

ENABLE_OTEL_TRACE = os.getenv("BKAPP_ENABLE_OTEL_TRACE", True if os.getenv("OTEL_BK_DATA_TOKEN") else False)

BK_APP_OTEL_INSTRUMENT_DB_API = os.getenv("BKAPP_OTEL_INSTRUMENT_DB_API", False)

NODE_CALLBACK_RETRY_TIMES = int(os.getenv("NODE_CALLBACK_RETRY_TIMES", os.getenv("BKAPP_NODE_CALLBACK_RETRY_TIMES", 5)))

# 蓝鲸插件开发地址
BK_PLUGIN_DEVELOP_URL = os.getenv("BK_PLUGIN_DEVELOP_URL", "")

# 蓝鲸插件授权过滤 APP
PLUGIN_DISTRIBUTOR_NAME = os.getenv("PLUGIN_DISTRIBUTOR_NAME", os.getenv("BKAPP_PLUGIN_DISTRIBUTOR_NAME"))

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
BK_APIGW_URL_TMPL = os.getenv("BK_API_URL_TMPL") or os.getenv("BKAPP_BK_API_URL_TMPL")

# 是否允许 celery worker 发送监控事件
CELERY_SEND_EVENTS = bool(os.getenv("CELERY_SEND_EVENTS", False))

# requests请求重试次数
REQUEST_RETRY_NUMBER = int(os.getenv("BKAPP_REQUEST_RETRY_NUMBER", 3))

# 默认请求重定向配置
NEED_HTTP_REDIRECT = os.getenv("BKAPP_NEED_HTTP_REDIRECT", False)
DEFAULT_REDIRECT_HOST = os.getenv("BKAPP_DEFAULT_REDIRECT_HOST", "")
REDIRECT_HOSTS = os.getenv("BKAPP_REDIRECT_HOSTS", "")
NOT_REDIRECT_HOSTS = os.getenv("BKAPP_NOT_REDIRECT_HOSTS", "")

# 数据清理配置
EXPIRED_TASK_CLEAN = False if os.getenv("BKAPP_EXPIRED_TASK_CLEAN") is None else True
EXPIRED_TASK_CLEAN_NUM_LIMIT = int(os.getenv("BKAPP_EXPIRED_TASK_CLEAN_NUM_LIMIT", 100))
TASK_EXPIRED_MONTH = int(os.getenv("BKAPP_TASK_EXPIRED_MONTH", 6))
MAX_EXPIRED_SESSION_CLEAN_NUM = int(os.getenv("BKAPP_MAX_EXPIRED_SESSION_CLEAN_NUM", 1000))
EXPIRED_SESSION_CLEAN_CRON = json.loads(
    os.getenv("BKAPP_EXPIRED_SESSION_CLEAN_CRON", '{"hour": "15", "minute": "0"}')
)  # UTC time

# V2引擎任务清理配置
ENABLE_CLEAN_EXPIRED_V2_TASK = bool(os.getenv("BKAPP_ENABLE_CLEAN_EXPIRED_V2_TASK", False))
CLEAN_EXPIRED_V2_TASK_CRON = tuple(os.getenv("BKAPP_CLEAN_EXPIRED_V2_TASK_CRON", "30 0 * * *").split())
V2_TASK_VALIDITY_DAY = int(os.getenv("BKAPP_V2_TASK_VALIDITY_DAY", 730))
CLEAN_EXPIRED_V2_TASK_BATCH_NUM = int(os.getenv("BKAPP_CLEAN_EXPIRED_V2_TASK_BATCH_NUM", 100))
CLEAN_EXPIRED_V2_TASK_INSTANCE = bool(os.getenv("BKAPP_CLEAN_EXPIRED_V2_TASK_INSTANCE", False))

# 是否启动swagger ui
ENABLE_SWAGGER_UI = os.getenv("BKAPP_ENABLE_SWAGGER_UI", False)

ENABLE_IPV6 = False if os.getenv("BKAPP_ENABLE_IPV6") is None else True
ENABLE_GSE_V2 = int(os.getenv("BKAPP_ENABLE_GSE_V2", 0)) == 1

# 流程最高嵌套层数
TEMPLATE_MAX_RECURSIVE_NUMBER = int(os.getenv("BKAPP_TEMPLATE_MAX_RECURSIVE_NUMBER", 200))

# 节点历史最大执行记录数
MAX_RECORDED_NODE_EXECUTION_TIMES = int(os.getenv("BKAPP_MAX_RECORDED_NODE_EXECUTION_TIMES", 5))

# 获取 PaaS 注入的蓝鲸域名
BKPAAS_BK_DOMAIN = os.getenv("BKPAAS_BK_DOMAIN", "") or os.getenv("BK_DOMAIN", "")


# 获取加密类型
BKPAAS_BK_CRYPTO_TYPE = (
    os.getenv("BKPAAS_BK_CRYPTO_TYPE", "")
    or os.getenv("BKAPP_BK_CRYPTO_TYPE", "")
    or os.getenv("BK_CRYPTO_TYPE")
    or "CLASSIC"
)

# 默认六个月
BKPAAS_TASK_LIST_STATUS_FILTER_DAYS = int(os.getenv("BKPAAS_TASK_LIST_STATUS_FILTER_DAYS", 180))

# 第三方插件特殊轮询时间配置
REMOTE_PLUGIN_FIX_INTERVAL_CODES_STR = os.getenv("BKAPP_REMOTE_PLUGIN_FIX_INTERVAL_CODES", "")
REMOTE_PLUGIN_FIX_INTERVAL_CODES = (
    REMOTE_PLUGIN_FIX_INTERVAL_CODES_STR.split(",") if REMOTE_PLUGIN_FIX_INTERVAL_CODES_STR else []
)
REMOTE_PLUGIN_FIX_INTERVAL = int(os.getenv("BKAPP_REMOTE_PLUGIN_FIX_INTERVAL", 60))

# 周期任务自动关闭扫描频率
PERIOD_TASK_TIMES = os.getenv("BKAPP_PERIOD_TASK_TIMES", 1)

# 周期任务自动关闭扫描周期
EXPIRED_SESSION_PERIOD_TASK_SCAN = json.loads(
    os.getenv("BKAPP_EXPIRED_SESSION_PERIOD_TASK_SCAN", '{"hour": "23", "minute": "0"}')
)

# 周期任务消息通知类型
PERIOD_TASK_MESSAGE_NOTIFY_TYPE = json.loads(os.getenv("PERIOD_TASK_MESSAGE_NOTIFY_TYPE", '["email"]'))
