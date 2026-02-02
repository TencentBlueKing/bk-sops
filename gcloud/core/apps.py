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
import os
import traceback

from django.apps import AppConfig
from django.conf import settings

import env

logger = logging.getLogger("root")


class CoreConfig(AppConfig):
    name = "gcloud.core"
    verbose_name = "GcloudCore"

    def ready(self):
        from gcloud.core.signals.handlers import business_post_save_handler  # noqa

        if hasattr(settings, "REDIS"):
            return

        try:
            from gcloud.core.models import EnvironmentVariables

            settings.REDIS = {
                "host": EnvironmentVariables.objects.get_var("BKAPP_REDIS_HOST")
                or EnvironmentVariables.objects.get_var("REDIS_HOST"),
                "port": EnvironmentVariables.objects.get_var("BKAPP_REDIS_PORT")
                or EnvironmentVariables.objects.get_var("REDIS_PORT"),
                "password": EnvironmentVariables.objects.get_var("BKAPP_REDIS_PASSWORD")
                or EnvironmentVariables.objects.get_var("REDIS_PASSWORD"),
                "service_name": EnvironmentVariables.objects.get_var("BKAPP_REDIS_SERVICE_NAME")
                or EnvironmentVariables.objects.get_var("REDIS_SERVICE_NAME"),
                "mode": EnvironmentVariables.objects.get_var("BKAPP_REDIS_MODE")
                or EnvironmentVariables.objects.get_var("REDIS_MODE"),
                "db": EnvironmentVariables.objects.get_var("BKAPP_REDIS_DB")
                or EnvironmentVariables.objects.get_var("REDIS_DB"),
                "sentinel_password": EnvironmentVariables.objects.get_var("BKAPP_REDIS_SENTINEL_PASSWORD")
                or EnvironmentVariables.objects.get_var("REDIS_SENTINEL_PASSWORD"),
                "ssl_ca_certs": EnvironmentVariables.objects.get_var("BKAPP_REDIS_CA")
                or EnvironmentVariables.objects.get_var("REDIS_CA"),
                "ssl_certfile": EnvironmentVariables.objects.get_var("BKAPP_REDIS_CERT")
                or EnvironmentVariables.objects.get_var("REDIS_CERT"),
                "ssl_keyfile": EnvironmentVariables.objects.get_var("BKAPP_REDIS_CERT_KEY")
                or EnvironmentVariables.objects.get_var("REDIS_CERT_KEY"),
                "ssl_cert_reqs": EnvironmentVariables.objects.get_var("BKAPP_REDIS_CERT_REQS")
                or EnvironmentVariables.objects.get_var("REDIS_CERT_REQS"),
                "ssl_check_hostname": EnvironmentVariables.objects.get_var("BKAPP_REDIS_CHECK_HOSTNAME")
                or EnvironmentVariables.objects.get_var("REDIS_CHECK_HOSTNAME"),
            }
        except Exception:
            logger.warning(traceback.format_exc())
            # first migrate, database may not have been migrated, so try get BKAPP_REDIS from env
            if "BKAPP_REDIS_HOST" in os.environ or "REDIS_HOST" in os.environ:
                settings.REDIS = {
                    "host": env.BKAPP_REDIS_HOST,
                    "port": env.BKAPP_REDIS_PORT,
                    "password": env.BKAPP_REDIS_PASSWORD,
                    "service_name": env.BKAPP_REDIS_SERVICE_NAME,
                    "mode": env.BKAPP_REDIS_MODE,
                    "db": env.BKAPP_REDIS_DB,
                    "sentinel_password": env.BKAPP_REDIS_SENTINEL_PASSWORD,
                }

                if not env.BKAPP_REDIS_CA:
                    return

                settings.REDIS.update(
                    {
                        "ssl_ca_certs": env.BKAPP_REDIS_CA,
                        "ssl_certfile": env.BKAPP_REDIS_CERT,
                        "ssl_keyfile": env.BKAPP_REDIS_CERT_KEY,
                    }
                )

                if not bool(env.BKAPP_REDIS_INSECURE_SKIP_VERIFY):
                    return

                settings.REDIS.update(
                    {
                        "ssl_cert_reqs": env.BKAPP_REDIS_CERT_REQS or "none",
                        "ssl_check_hostname": bool(env.BKAPP_REDIS_CHECK_HOSTNAME) or False,
                    }
                )
