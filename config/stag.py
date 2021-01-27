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
    from blueapps.patch.settings_paas_services import *  # noqaJobExecuteTaskComponent

import env


# 预发布环境
RUN_MODE = "STAGING"

BK_IAM_SYNC_TEMPLATES = True

BK_IAM_RESOURCE_API_HOST = env.BK_IAM_RESOURCE_API_HOST

CSRF_COOKIE_NAME = APP_CODE + "_csrftoken"

LOGGING["loggers"]["iam"] = {
    "handlers": ["component"],
    "level": "DEBUG",
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

# 多环境需要，celery的handler需要动态获取
LOGGING["loggers"]["celery_and_engine_component"] = {
    "handlers": ["engine_component", LOGGING["loggers"]["celery"]["handlers"][0]],
    "level": "INFO",
    "propagate": True,
}
