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
import requests

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import permissions

from gcloud.conf import settings
from gcloud import err_code
from gcloud.contrib.template_maker.serializers import TemplateSharedRecordSerializer
from gcloud.contrib.template_maker.models import TemplateSharedRecord
from gcloud.core.apis.drf.serilaziers.task_template import TaskTemplateSerializer, TaskTemplateListSerializer
from gcloud.taskflow3.models import TaskTemplate
from gcloud.core.apis.drf.viewsets.base import GcloudModelViewSet


class TemplateMarkerPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        template_id = view.kwargs.get("pk")
        project_id = request.GET.get("project_id")

        if not template_id or not project_id:
            logging.warning("template_id is required.")
            return False
        try:
            TemplateSharedRecord.objects.get(template_id=template_id, project_id=project_id)
        except Exception:
            logging.warning("template_id {} does not exist.".format(template_id))
            return False
        return True


class SharedTemplatePermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if not settings.ENABLE_TEMPLATE_MARKET:
            return False
        return True


class TemplateMarketViewSet(GcloudModelViewSet):
    queryset = TaskTemplate.objects.filter(pipeline_template__isnull=False, is_deleted=False)
    permission_classes = [permissions.IsAuthenticated, TemplateMarkerPermission]

    def get_serializer_class(self):
        if self.action == "list":
            return TaskTemplateListSerializer
        return TaskTemplateSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        return Response(serializer.data)


class SharedTemplateViewSet(viewsets.ModelViewSet):
    queryset = TemplateSharedRecord.objects.all()
    serializer_class = TemplateSharedRecordSerializer
    permission_classes = [permissions.IsAuthenticated, SharedTemplatePermission]

    def _get_market_routing(self, market_url):
        return f"{settings.FLOW_MARKET_API_URL}/{market_url}"

    def retrieve(self, request, *args, **kwargs):
        project_id = kwargs.get("pk")
        template_id = request.GET.get("template_id")

        url = self._get_market_routing("market/details/")
        data = {"project_id": project_id, "template_id": template_id}

        # 根据业务id和模板id从第三方接口获取模板详情
        result = requests.post(url, data=data)

        if not result or result.status_code != 200:
            logging.exception("Get market template details from third party fails")
            return Response(
                {
                    "result": False,
                    "message": "Get market template details from third party fails",
                    "code": err_code.OPERATION_FAIL.code,
                }
            )

        return Response(result.json())

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

        # 执行第三方接口调用
        url = self._get_market_routing("prod/api/")
        data = {}
        headers = None
        result = requests.post(url, headers=headers, data=data)
        if not result:
            logging.exception("Sharing template to SRE store fails")
            return Response(
                {
                    "result": False,
                    "message": "Sharing template to SRE store fails",
                    "code": err_code.OPERATION_FAIL.code,
                },
            )

        self.perform_create(serializer)

        return Response({"result": True, "message": "Share template successfully", "code": err_code.SUCCESS.code})
