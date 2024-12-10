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

from rest_framework import permissions

from gcloud.conf import settings
from gcloud.contrib.template_market.models import TemplateSharedRecord


class TemplatePreviewPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        template_id = request.GET.get("template_id")
        project_id = request.GET.get("project_id")

        if not template_id or not project_id:
            logging.warning("Missing required parameters.")
            return False

        record = TemplateSharedRecord.objects.filter(template_id=template_id, project_id=project_id).first()
        if record is None:
            logging.warning("template_id {} does not exist.".format(template_id))
            return False

        return True


class SharedProcessTemplatePermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return settings.ENABLE_TEMPLATE_MARKET
