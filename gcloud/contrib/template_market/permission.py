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

from django.db.models import Q
from rest_framework import permissions

from gcloud.conf import settings
from gcloud.contrib.template_market.models import TemplateSharedRecord
from gcloud.iam_auth import IAMMeta
from gcloud.iam_auth.utils import iam_multi_resource_auth_or_raise


class TemplatePreviewPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        try:
            template_id = int(request.GET.get("template_id"))
            project_id = int(request.GET.get("project_id"))
        except (TypeError, ValueError):
            logging.warning("Missing or invalid required parameters.")
            return False

        record = TemplateSharedRecord.objects.filter(
            Q(project_id=project_id) & Q(templates__contains=[template_id])
        ).first()
        if record is None:
            logging.warning("The specified template could not be found")
            return False

        return True


class SharedProcessTemplatePermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.action in ["create", "partial_update"]:
            username = request.user.username
            serializer = view.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)

            template_id_list = serializer.validated_data["templates"]

            iam_multi_resource_auth_or_raise(
                username, IAMMeta.FLOW_EDIT_ACTION, template_id_list, "resources_list_for_flows"
            )

        return settings.ENABLE_TEMPLATE_MARKET
