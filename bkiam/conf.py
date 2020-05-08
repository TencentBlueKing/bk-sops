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

try:
    from django.conf import settings

    APP_CODE = settings.APP_CODE
    SECRET_KEY = settings.SECRET_KEY
    SYSTEM_ID = getattr(settings, 'BK_IAM_SYSTEM_ID', APP_CODE)
    SYSTEM_NAME = getattr(settings, 'BK_IAM_SYSTEM_NAME', APP_CODE)
    BK_IAM_INNER_HOST = getattr(settings, 'BK_IAM_INNER_HOST', '')
    BK_IAM_API_VERSION = getattr(settings, 'BK_IAM_API_VERSION', 'v1')

except Exception:
    APP_CODE = ''
    SECRET_KEY = ''
    SYSTEM_ID = ''
    SYSTEM_NAME = ''
    BK_IAM_INNER_HOST = ''
    BK_IAM_API_VERSION = 'v1'
