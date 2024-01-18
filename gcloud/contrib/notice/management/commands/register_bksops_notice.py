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

from django.core.management import call_command
from django.core.management.base import BaseCommand

import env
from gcloud.core.models import EnvironmentVariables

logger = logging.getLogger("root")


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        # 非PAAS v3 无法开启通知中心
        if not env.IS_PAAS_V3:
            EnvironmentVariables.objects.update_or_create(
                defaults={"value": 0}, key="ENABLE_NOTICE_CENTER"
            )
            print("[bk-sops]current version is not open v3,skip register_bksops_notice")
            return
        try:
            call_command("register_application")
            EnvironmentVariables.objects.update_or_create(
                defaults={"value": 1}, key="ENABLE_NOTICE_CENTER"
            )
        except Exception as e:
            logger.exception("[register_bksops_notice] err: {}".format(e))
            EnvironmentVariables.objects.update_or_create(
                defaults={"value": 0}, key="ENABLE_NOTICE_CENTER"
            )
