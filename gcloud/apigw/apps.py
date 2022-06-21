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

import logging
from django.apps import AppConfig

from gcloud.conf import settings
import env

logger = logging.getLogger("root")


class ApiConfig(AppConfig):
    name = "gcloud.apigw"
    verbose_name = "GcloudApigw"
    label = "gcloud_apigw"

    def ready(self):
        if not env.IS_PAAS_V3:
            logger.info("[API]get esb public key")
            get_client_by_user = settings.ESB_GET_CLIENT_BY_USER
            client = get_client_by_user(settings.SYSTEM_USE_API_ACCOUNT)
            esb_result = client.esb.get_api_public_key()
            if esb_result["result"]:
                esb_public_key = esb_result["data"]["public_key"]
                try:
                    from apigw_manager.apigw.helper import PublicKeyManager

                    PublicKeyManager().set("bk-esb", esb_public_key)
                    PublicKeyManager().set("apigw", esb_public_key)
                except Exception:
                    logger.exception("[API] apigw_manager_context table is not migrated")
            else:
                logger.warning("[API] get esb public key error: %s" % esb_result["message"])
