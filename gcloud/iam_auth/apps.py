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

from django.apps import AppConfig
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from gcloud.iam_auth.domains import build_iam_v4_api_url


def validate_settings():
    """Validate IAM V4 configuration without making a network request."""

    chunk_size = settings.IAM_V4_BATCH_AUTH_CHUNK_SIZE
    if not isinstance(chunk_size, int) or chunk_size < 1 or chunk_size > 20:
        raise ImproperlyConfigured("IAM_V4_BATCH_AUTH_CHUNK_SIZE must be between 1 and 20")

    timeout = settings.IAM_V4_REQUEST_TIMEOUT
    if not isinstance(timeout, int) or timeout < 1:
        raise ImproperlyConfigured("IAM_V4_REQUEST_TIMEOUT must be a positive integer")

    tenant_header = settings.IAM_V4_TENANT_HEADER
    if not isinstance(tenant_header, str) or not tenant_header.strip():
        raise ImproperlyConfigured("IAM_V4_TENANT_HEADER must not be empty")

    if getattr(settings, "RUN_MODE", "") in {"PRODUCT", "STAGING"}:
        required = {
            "BK_APP_CODE": settings.BK_APP_CODE,
            "BK_APP_SECRET": settings.BK_APP_SECRET,
            "BK_IAM_SYSTEM_ID": settings.BK_IAM_SYSTEM_ID,
            "BKIAM_APIGW_NAME": settings.BKIAM_APIGW_NAME,
            "IAM V4 endpoint": build_iam_v4_api_url(),
            "IAM V4 callback host": getattr(settings, "BK_IAM_RESOURCE_API_HOST", ""),
            "IAM V4 model tenant": getattr(settings, "IAM_V4_MODEL_REGISTRATION_TENANT_ID", ""),
        }
        missing = [name for name, value in required.items() if not value]
        if missing:
            raise ImproperlyConfigured("missing IAM V4 settings: {}".format(", ".join(missing)))


class IamAuthConfig(AppConfig):
    name = "gcloud.iam_auth"

    def ready(self):
        # V4-only 首期不注册 V3 creator grant signal / Celery grant 链路。
        validate_settings()
