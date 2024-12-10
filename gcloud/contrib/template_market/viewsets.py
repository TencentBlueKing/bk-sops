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
import json
import requests
import logging

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import permissions

from drf_yasg.utils import swagger_auto_schema
from gcloud.conf import settings
from gcloud import err_code
from gcloud.contrib.template_market.serializers import TemplateSharedRecordSerializer, TemplatePreviewSerializer
from gcloud.contrib.template_market.models import TemplateSharedRecord
from gcloud.taskflow3.models import TaskTemplate
from gcloud.contrib.template_market.permission import TemplatePreviewPermission, SharedProcessTemplatePermission


class TemplatePreviewViewSet(viewsets.ViewSet):
    queryset = TaskTemplate.objects.filter(pipeline_template__isnull=False, is_deleted=False)
    serializer_class = TemplatePreviewSerializer
    permission_classes = [permissions.IsAuthenticated, TemplatePreviewPermission]

    def retrieve(self, request, *args, **kwargs):
        instance = self.queryset.get(id=request.GET.get("template_id"), project_id=request.GET.get("project_id"))
        serializer = self.serializer_class(instance)

        return Response({"result": True, "data": serializer.data, "code": err_code.SUCCESS.code})


class SharedProcessTemplateViewSet(viewsets.ViewSet):
    queryset = TemplateSharedRecord.objects.all()
    serializer_class = TemplateSharedRecordSerializer
    permission_classes = [permissions.IsAuthenticated, SharedProcessTemplatePermission]

    def _get_market_routing(self, market_url):
        return f"{settings.TEMPLATE_MARKET_API_URL}/{market_url}"

    def retrieve(self, request, *args, **kwargs):
        project_id = request.GET.get("project_id")
        template_id = request.GET.get("template_id")

        template_shared_obj = TemplateSharedRecord.objects.filter(
            project_id=project_id, template_id=template_id
        ).first()

        if not template_shared_obj:
            logging.exception(f"Template shared record not found, project_id: {project_id}, template_id: {template_id}")
            return Response(
                {
                    "result": False,
                    "message": "Template shared record not found",
                    "code": err_code.CONTENT_NOT_EXIST.code,
                }
            )
        url = self._get_market_routing(f"sre_scene/flow_template_scene/{template_shared_obj.scene_instance_id}/")
        result = requests.get(url=url)
        if not result.status_code == 200:
            logging.exception(f"Get template information from market failed, error code: {result.status_code}")
            return Response(
                {"result": False, "message": "Get template information failed", "code": err_code.OPERATION_FAIL.code}
            )

        return Response({"result": True, "data": result.json(), "code": err_code.SUCCESS.code})

    @swagger_auto_schema(request_body=TemplateSharedRecordSerializer)
    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        project_id = serializer.validated_data["project_id"]
        template_id = serializer.validated_data["template_id"]

        task_template_obj = TaskTemplate.objects.filter(project_id=project_id, id=template_id).first()
        if not task_template_obj:
            logging.exception(f"Template with project_id {project_id} and template_id {template_id} not found.")
            return Response({"result": False, "message": "Template not found", "code": err_code.CONTENT_NOT_EXIST.code})

        url = self._get_market_routing("sre_scene/flow_template_scene/")

        data = {
            "name": serializer.validated_data["name"],
            "code": serializer.validated_data["code"],
            "category": serializer.validated_data["category"],
            "risk_level": serializer.validated_data["risk_level"],
            "labels": serializer.validated_data["labels"],
            "source_system": "bk_sops",
            "project_code": project_id,
            "templates": json.dumps([{"id": template_id, "name": task_template_obj.name}]),
            "usage_content": {"content": serializer.validated_data["usage_content"]},
        }
        try:
            result = requests.post(url, data=data)
            if result.status_code != 200:
                return Response(
                    {
                        "result": False,
                        "message": "Failed to share template to sre store",
                        "code": err_code.OPERATION_FAIL.code,
                    }
                )
            response_data = result.json()
            TemplateSharedRecord.create(
                project_id=project_id,
                template_id=template_id,
                scene_instance_id=response_data["data"]["id"],
                creator=serializer.validated_data.get("creator"),
                extra_info=serializer.validated_data.get("extra_info"),
            )
            return Response(
                {
                    "result": True,
                    "data": response_data,
                    "message": "Share template successfully",
                    "code": err_code.SUCCESS.code,
                }
            )
        except Exception as e:
            logging.exception("Share template failed: %s", e)
            return Response({"result": False, "message": "Share template failed", "code": err_code.OPERATION_FAIL.code})
