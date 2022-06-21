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
from django.conf import settings

USE_PLUGIN_SERVICE = os.getenv("BKAPP_USE_PLUGIN_SERVICE", False)

PLUGIN_SERVICE_APIGW_APP_CODE = os.getenv("BKAPP_PLUGIN_SERVICE_APIGW_APP_CODE", settings.APP_CODE)
PLUGIN_SERVICE_APIGW_APP_SECRET = os.getenv("BKAPP_PLUGIN_SERVICE_APIGW_APP_SECRET", settings.APP_TOKEN)

PAASV3_APIGW_API_TOKEN = os.getenv("BKAPP_PAASV3_APIGW_API_TOKEN")
APIGW_ENVIRONMENT = os.getenv("BKAPP_APIGW_ENVIRONMENT", settings.ENVIRONMENT)
APIGW_NETWORK_PROTOCAL = os.getenv("BKAPP_APIGW_NETWORK_PROTOCAL", "http")
APIGW_URL_SUFFIX = os.getenv("BKAPP_APIGW_URL_SUFFIX")

BKAPP_INVOKE_PAAS_RETRY_NUM = int(os.getenv("BKAPP_REQUEST_PAAS_RETRY_NUM", 3))

APIGW_USER_AUTH_KEY_NAME = os.getenv("BKAPP_APIGW_USER_AUTH_KEY_NAME", "bk_token")
