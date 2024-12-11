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
import logging

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import permissions

from gcloud import err_code
from gcloud.conf import settings
from drf_yasg.utils import swagger_auto_schema
from gcloud.contrib.template_market.serializers import (
    TemplateSharedRecordSerializer,
    TemplatePreviewSerializer,
    TemplateProjectBaseSerializer,
)
from gcloud.contrib.template_market.models import TemplateSharedRecord
from gcloud.taskflow3.models import TaskTemplate
from gcloud.contrib.template_market.utils import MarketAPIClient
from gcloud.contrib.template_market.permission import TemplatePreviewPermission, SharedProcessTemplatePermission


class TemplatePreviewViewSet(viewsets.ViewSet):
    queryset = TaskTemplate.objects.filter(pipeline_template__isnull=False, is_deleted=False)
    serializer_class = TemplatePreviewSerializer
    permission_classes = [permissions.IsAuthenticated, TemplatePreviewPermission]

    def retrieve(self, request, *args, **kwargs):
        request_serializer = TemplateProjectBaseSerializer(data=request.GET)
        request_serializer.is_valid(raise_exception=True)

        template_id = request_serializer.validated_data["template_id"]
        project_id = request_serializer.validated_data["project_id"]

        instance = self.queryset.get(id=template_id, project_id=project_id)
        serializer = self.serializer_class(instance)

        return Response({"result": True, "data": serializer.data, "code": err_code.SUCCESS.code})


class SharedProcessTemplateViewSet(viewsets.ViewSet):
    queryset = TemplateSharedRecord.objects.all()
    serializer_class = TemplateSharedRecordSerializer
    permission_classes = [permissions.IsAuthenticated, SharedProcessTemplatePermission]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.market_client = MarketAPIClient()

    def _build_template_data(self, serializer):

        data = {
            "name": serializer.validated_data["name"],
            "code": serializer.validated_data["code"],
            "category": serializer.validated_data["category"],
            "risk_level": serializer.validated_data["risk_level"],
            "usage_id": serializer.validated_data["usage_id"],
            "labels": serializer.validated_data["labels"],
            "source_system": "bk_sops",
            "project_code": serializer.validated_data["project_id"],
            "templates": json.dumps(serializer.validated_data["templates"]),
            "usage_content": serializer.validated_data["usage_content"],
        }
        scene_shared_id = serializer.validated_data.get("id")
        if scene_shared_id:
            data["id"] = scene_shared_id
        return data

    def _get_processes_count(self, templates):
        template_id_list = [template.get("id") for template in templates]

        template_objs = TaskTemplate.objects.filter(id__in=template_id_list)

        total_count = 0
        for template in template_objs:
            activities = template.pipeline_tree.get("activities", [])
            total_count += len(activities)

        return total_count

    def list(self, request, *args, **kwargs):
        response_data = self.market_client.get_template_list()

        if not response_data["result"]:
            logging.exception(f"Get template information from market failed, error code: {response_data.get('code')}")
            return Response(
                {"result": False, "message": "Get template information failed", "code": err_code.OPERATION_FAIL.code}
            )

        return Response({"result": True, "data": response_data, "code": err_code.SUCCESS.code})

    @swagger_auto_schema(request_body=TemplateSharedRecordSerializer)
    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        template_count = self._get_processes_count(serializer.validated_data["templates"])
        if template_count > settings.MAX_NUMBER_SHARED_PROCESSES:
            return Response(
                {
                    "result": False,
                    "message": "The number of selected templates exceeds the limit",
                    "code": err_code.OPERATION_FAIL.code,
                }
            )

        data = self._build_template_data(serializer)
        try:
            response_data = self.market_client.create_template(data)
            if not response_data.get("result"):
                return Response(
                    {
                        "result": False,
                        "message": "Failed to share template to sre store",
                        "code": err_code.OPERATION_FAIL.code,
                    }
                )
            serializer.validated_data["id"] = response_data["data"]["id"]
            serializer.create(serializer.validated_data)
            return Response(
                {
                    "result": True,
                    "data": "response_data",
                    "message": "Share template successfully",
                    "code": err_code.SUCCESS.code,
                }
            )
        except Exception as e:
            logging.exception("Share template failed: %s", e)
            return Response({"result": False, "message": "Share template failed", "code": err_code.OPERATION_FAIL.code})

    @swagger_auto_schema(request_body=TemplateSharedRecordSerializer)
    def partial_update(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        scene_shared_id = serializer.validated_data.get("id")

        data = self._build_template_data(serializer)
        try:
            response_data = self.market_client.patch_template(data, scene_shared_id)
            if not response_data.get("result"):
                return Response(
                    {
                        "result": False,
                        "message": "Update template to sre store failed",
                        "code": err_code.OPERATION_FAIL.code,
                    }
                )
            instance = self.queryset.get(scene_shared_id=scene_shared_id)
            serializer.update(instance, serializer.validated_data)
            return Response(
                {
                    "result": True,
                    "data": response_data,
                    "message": "Share template successfully",
                    "code": err_code.SUCCESS.code,
                }
            )
        except Exception as e:
            logging.exception("Failed to update scene template: %s", e)
            return Response(
                {"result": False, "message": "Failed to update scene template", "code": err_code.OPERATION_FAIL.code}
            )
