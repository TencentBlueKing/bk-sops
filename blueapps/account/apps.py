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

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.core.cache import caches

from blueapps.utils import get_client_by_user
from blueapps.utils.logger import logger
from blueapps.account.conf import APIGW_CACHE_KEY, APIGW_CACHE_EXPIRES

cache = caches["login_db"]


class AccountConfig(AppConfig):

    name = "blueapps.account"
    verbose_name = _("account")

    def ready(self):
        self.get_api_public_key()
        return True

    @staticmethod
    def get_api_public_key():
        # return if APIGW_ENABLED is not set
        if not hasattr(settings, "APIGW_ENABLED") or not bool(settings.APIGW_ENABLED):
            return

        # return if public key is configured
        if hasattr(settings, "APIGW_PUBLIC_KEY"):
            return

        # get api key by cache
        api_public_key = cache.get(APIGW_CACHE_KEY)
        if api_public_key:
            message = "[ESB][JWT]get esb api public key success (from cache)"
            print(message, flush=True)
            logger.info(message)
            settings.APIGW_PUBLIC_KEY = api_public_key
            return api_public_key

        # get api key by api
        client = get_client_by_user(getattr(settings, "APIGW_API_ACCOUNT", "admin"))
        esb_result = client.esb.get_api_public_key()
        if esb_result["result"]:
            api_public_key = esb_result["data"]["public_key"]
            settings.APIGW_PUBLIC_KEY = api_public_key
            cache.set(APIGW_CACHE_KEY, api_public_key, APIGW_CACHE_EXPIRES)
            message = "[ESB][JWT]get esb api public key success (from realtime api)"
            print(message, flush=True)
            logger.info(message)
        else:
            message = f'[ESB][JWT]get esb api public key error:{esb_result["message"]}'
            print(message, flush=True)
            logger.warning(message)
            raise Exception(message)
