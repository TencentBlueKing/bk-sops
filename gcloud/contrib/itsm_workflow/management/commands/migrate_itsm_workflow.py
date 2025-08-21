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
from io import BytesIO

from django.conf import settings
from django.core.management.base import BaseCommand

from packages.bkapi.bk_itsm4.shortcuts import get_client_by_username

logger = logging.getLogger("root")


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("-t", "--tenant_id", help="租户ID", type=str)

    def handle(self, *args, **options):
        if not settings.ENABLE_MULTI_TENANT_MODE:
            return

        tenant_id = options.get("tenant_id")

        client = get_client_by_username("bk_admin", stage=settings.BK_APIGW_STAGE_NAME)
        # 注册itsm system
        try:
            client.api.system_create(
                {"name": settings.APP_CODE, "code": settings.APP_CODE, "token": settings.SECRET_KEY},
                headers={"X-Bk-Tenant-Id": tenant_id},
            )
        except Exception as e:
            logger.error(e)

        # migrate itsm workflow
        template_path = os.path.join(
            settings.BASE_DIR, "gcloud/contrib/itsm_workflow/template/itsm_migrate_template.json"
        )
        try:
            with open(template_path, "r") as file:
                template = file.read()
                tenant_template = template.replace("__tenant_id__", tenant_id)

                file_obj = BytesIO(tenant_template.encode("utf-8"))
                files = {"file": file_obj}
                client.api.system_migrate(
                    headers={"X-Bk-Tenant-Id": tenant_id},
                    files=files,
                )
        except Exception as e:
            logger.error(e)
