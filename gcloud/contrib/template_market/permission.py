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

from iam.exceptions import MultiAuthFailedException
from rest_framework import permissions

from gcloud.conf import settings
from gcloud.contrib.template_market.models import TemplateSharedRecord
from gcloud.contrib.template_market.serializers import TemplateProjectBaseSerializer
from gcloud.iam_auth import IAMMeta
from gcloud.iam_auth.utils import iam_multi_resource_auth_or_raise


class TemplatePreviewPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        serializer = TemplateProjectBaseSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        template_id = int(serializer.validated_data["template_id"])
        project_id = int(serializer.validated_data["project_id"])
        record = TemplateSharedRecord.objects.filter(project_id=project_id, template_id=template_id).first()
        if record is None:
            logging.warning("The specified template could not be found")
            return False

        return True


class SharedTemplateRecordPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if not settings.ENABLE_TEMPLATE_MARKET:
            return False

        if view.action in ["create", "partial_update"]:
            username = request.user.username
            serializer = view.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)

            template_id_list = serializer.validated_data["templates"]
            try:
                iam_multi_resource_auth_or_raise(
                    username, IAMMeta.FLOW_EDIT_ACTION, template_id_list, "resources_list_for_flows"
                )
            except MultiAuthFailedException:
                logging.exception("Template permission verification failed")
                return False

        return True
