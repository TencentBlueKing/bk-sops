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

from config import RUN_VER

if RUN_VER == "open":
    from blueapps.patch.settings_open_saas import *  # noqa
else:
    from blueapps.patch.settings_paas_services import *  # noqa

# 正式环境
RUN_MODE = "PRODUCT"

BK_IAM_SYNC_TEMPLATES = True

BK_IAM_RESOURCE_API_HOST = os.getenv("BKAPP_IAM_RESOURCE_API_HOST", "{}{}".format(BK_PAAS_INNER_HOST, SITE_URL))
# 权限中心 SDK 无权限时不返回 499 的请求路径前缀配置
BK_IAM_API_PREFIX = os.getenv("BKAPP_BK_IAM_API_PREFIX", SITE_URL + "apigw")

LOGGING["loggers"]["iam"] = {
    "handlers": ["component"],
    "level": "INFO",
    "propagate": True,
}

LOGGING["handlers"]["engine_component"] = {
    "class": "pipeline.log.handlers.EngineContextLogHandler",
    "formatter": "verbose",
}

LOGGING["loggers"]["component"] = {
    "handlers": ["component", "engine_component"],
    "level": "DEBUG",
    "propagate": True,
}

LOGGING["formatters"]["light"] = {"format": "%(message)s"}

LOGGING["handlers"]["engine"] = {
    "class": "pipeline.log.handlers.EngineLogHandler",
    "formatter": "light",
}

LOGGING["loggers"]["pipeline.logging"] = {
    "handlers": ["engine"],
    "level": "INFO",
    "propagate": True,
}
