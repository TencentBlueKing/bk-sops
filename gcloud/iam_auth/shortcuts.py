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

from django.conf import settings
from iam import IAM, DummyIAM
from iam.api.client import Client

import env


def get_iam_client(tenant_id=""):
    app_code = env.BKAPP_SOPS_IAM_APP_CODE
    app_secret = env.BKAPP_SOPS_IAM_APP_SECRET_KEY
    if settings.BK_IAM_SKIP:
        return DummyIAM(app_code, app_secret, bk_apigateway_url=settings.BK_IAM_APIGW_HOST, bk_tenant_id=tenant_id)
    return IAM(app_code, app_secret, bk_apigateway_url=settings.BK_IAM_APIGW_HOST, bk_tenant_id=tenant_id)


def get_iam_api_client(tenant_id):
    app_code = env.BKAPP_SOPS_IAM_APP_CODE
    app_secret = env.BKAPP_SOPS_IAM_APP_SECRET_KEY
    return Client(app_code, app_secret, bk_apigateway_url=settings.BK_IAM_APIGW_HOST, bk_tenant_id=tenant_id)
