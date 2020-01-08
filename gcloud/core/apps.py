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

import os
import logging
import traceback

from django.apps import AppConfig
from django.conf import settings

logger = logging.getLogger('root')


class CoreConfig(AppConfig):
    name = 'gcloud.core'
    verbose_name = 'GcloudCore'

    def ready(self):
        from gcloud.core.signals.handlers import business_post_save_handler  # noqa
        if not hasattr(settings, 'REDIS'):
            try:
                from gcloud.core.models import EnvironmentVariables
                settings.REDIS = {
                    'host': EnvironmentVariables.objects.get_var('BKAPP_REDIS_HOST'),
                    'port': EnvironmentVariables.objects.get_var('BKAPP_REDIS_PORT'),
                    'password': EnvironmentVariables.objects.get_var('BKAPP_REDIS_PASSWORD'),
                    'service_name': EnvironmentVariables.objects.get_var('BKAPP_REDIS_SERVICE_NAME'),
                    'mode': EnvironmentVariables.objects.get_var('BKAPP_REDIS_MODE'),
                    'db': EnvironmentVariables.objects.get_var('BKAPP_REDIS_DB'),
                }
            except Exception:
                logger.warning(traceback.format_exc())
                # first migrate, database may not have been migrated, so try get BKAPP_REDIS from env
                if 'BKAPP_REDIS_HOST' in os.environ:
                    settings.REDIS = {
                        'host': os.getenv('BKAPP_REDIS_HOST'),
                        'port': os.getenv('BKAPP_REDIS_PORT'),
                        'password': os.getenv('BKAPP_REDIS_PASSWORD'),
                        'service_name': os.getenv('BKAPP_REDIS_SERVICE_NAME'),
                        'mode': os.getenv('BKAPP_REDIS_MODE'),
                        'db': os.getenv('BKAPP_REDIS_DB'),
                    }
