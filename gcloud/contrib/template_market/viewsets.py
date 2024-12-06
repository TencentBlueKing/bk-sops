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

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import permissions

from gcloud.conf import settings
from gcloud import err_code
from gcloud.contrib.template_market.serializers import TemplateSharedRecordSerializer
from gcloud.contrib.template_market.models import TemplateSharedRecord
from gcloud.core.apis.drf.serilaziers.task_template import TaskTemplateSerializer
from gcloud.taskflow3.models import TaskTemplate


class StoreTemplatePermission(permissions.BasePermission):
    def has_permission(self, request, view):
        template_id = view.kwargs.get("pk")
        project_id = request.GET.get("project_id")

        if not template_id or not project_id:
            logging.warning("Missing required parameters.")
            return False
        try:
            TemplateSharedRecord.objects.get(template_id=template_id, project_id=project_id)
        except Exception:
            logging.warning("template_id {} does not exist.".format(template_id))
            return False
        return True


class SharedProcessTemplatePermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if not settings.ENABLE_TEMPLATE_MARKET:
            return False
        return True


class StoreTemplateViewSet(viewsets.ViewSet):
    queryset = TaskTemplate.objects.filter(pipeline_template__isnull=False, is_deleted=False)
    serializer_class = TaskTemplateSerializer
    permission_classes = [permissions.IsAuthenticated, StoreTemplatePermission]

    def retrieve(self, request, *args, **kwargs):
        instance = self.queryset.get(id=kwargs["pk"], project_id=request.GET.get("project_id"))
        serializer = self.serializer_class(instance)

        return Response(serializer.data)


class SharedProcessTemplateViewSet(viewsets.ModelViewSet):
    queryset = TemplateSharedRecord.objects.all()
    serializer_class = TemplateSharedRecordSerializer
    permission_classes = [permissions.IsAuthenticated, SharedProcessTemplatePermission]

    def _get_market_routing(self, market_url):
        return f"{settings.TEMPLATE_MARKET_API_URL}/{market_url}"

    def retrieve(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.GET)
        serializer.is_valid(raise_exception=True)

        project_id = serializer.validated_data.get("project_id")
        template_id = serializer.validated_data.get("template_id")

        data = {"project_id": project_id, "template_id": template_id}

        # todo: 调用第三方接口查询信息

        return Response({"result": True, "data": data, "code": err_code.SUCCESS.code})

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        project_id = serializer.validated_data.get("project_id")
        template_id = serializer.validated_data.get("template_id")

        try:
            TaskTemplate.objects.get(project_id=project_id, id=template_id)
        except TaskTemplate.DoesNotExist:
            logging.warning(f"Template with project_id {project_id} and template_id {template_id} not found.")
            return Response({"result": False, "message": "Template not found", "code": err_code.OPERATION_FAIL.code})

        # todo: 调用第三方接口实现共享

        self.perform_create(serializer)

        return Response({"result": True, "message": "Share template successfully", "code": err_code.SUCCESS.code})
