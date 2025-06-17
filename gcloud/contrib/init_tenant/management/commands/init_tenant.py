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

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand

logger = logging.getLogger("root")


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("-t", "--tenant_id", help="租户ID", type=str)

    def handle(self, *args, **options):
        tenant_id = options.get("tenant_id")
        # 注册itsm workflow
        if settings.ENABLE_MULTI_TENANT_MODE:
            call_command("migrate_itsm_workflow", "--tenant_id", tenant_id)

        # 其他初始化操作

        logger.info(f"initialize tenant {tenant_id} success")
