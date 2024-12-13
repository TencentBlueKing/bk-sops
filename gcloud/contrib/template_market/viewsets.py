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
from rest_framework.views import APIView
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
from gcloud.contrib.template_market.clients import MarketAPIClient
from gcloud.contrib.template_market.permission import TemplatePreviewPermission, SharedTemplateRecordPermission


class TemplatePreviewAPIView(APIView):
    queryset = TaskTemplate.objects.filter(pipeline_template__isnull=False, is_deleted=False)
    serializer_class = TemplatePreviewSerializer
    permission_classes = [permissions.IsAuthenticated, TemplatePreviewPermission]

    def get(self, request, *args, **kwargs):
        request_serializer = TemplateProjectBaseSerializer(data=request.query_params)
        request_serializer.is_valid(raise_exception=True)

        template_id = request_serializer.validated_data["template_id"]
        project_id = request_serializer.validated_data["project_id"]

        instance = self.queryset.get(id=template_id, project_id=project_id)
        serializer = self.serializer_class(instance)

        return Response({"result": True, "data": serializer.data, "code": err_code.SUCCESS.code})


class SharedTemplateRecordsViewSet(viewsets.ViewSet):
    queryset = TemplateSharedRecord.objects.all()
    serializer_class = TemplateSharedRecordSerializer
    permission_classes = [permissions.IsAuthenticated, SharedTemplateRecordPermission]

    market_client = MarketAPIClient()

    def _build_template_data(self, serializer, **kwargs):
        templates = TaskTemplate.objects.filter(id__in=serializer.validated_data["template_ids"], is_deleted=False)
        template_info = [{"id": template.id, "name": template.name} for template in templates]
        data = {
            "name": serializer.validated_data["name"],
            "code": serializer.validated_data["code"],
            "category": serializer.validated_data["category"],
            "risk_level": serializer.validated_data["risk_level"],
            "usage_id": serializer.validated_data["usage_id"],
            "labels": serializer.validated_data["labels"],
            "source_system": settings.APP_CODE,
            "project_code": serializer.validated_data["project_id"],
            "templates": json.dumps(template_info),
            "usage_content": serializer.validated_data["usage_content"],
        }
        market_record_id = kwargs.get("market_record_id")
        if market_record_id:
            data["id"] = market_record_id
        return data

    def list(self, request, *args, **kwargs):
        response_data = self.market_client.get_market_template_list()

        if not response_data["result"]:
            logging.exception("Failed to obtain the market template list")
            return Response(
                {
                    "result": False,
                    "message": "Failed to obtain the market template list",
                    "code": err_code.OPERATION_FAIL.code,
                }
            )
        return Response({"result": True, "data": response_data, "code": err_code.SUCCESS.code})

    @swagger_auto_schema(request_body=TemplateSharedRecordSerializer)
    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = self._build_template_data(serializer)
        response_data = self.market_client.create_market_template_record(data)
        if not response_data.get("result"):
            return Response(
                {
                    "result": False,
                    "message": "Failed to create market template record",
                    "code": err_code.OPERATION_FAIL.code,
                }
            )
        TemplateSharedRecord.objects.update_shared_record(
            project_id=int(serializer.validated_data["project_id"]),
            new_template_ids=serializer.validated_data["template_ids"],
            market_record_id=response_data["data"]["id"],
            creator=serializer.validated_data["creator"],
        )
        return Response({"result": True, "data": response_data, "code": err_code.SUCCESS.code})

    @swagger_auto_schema(request_body=TemplateSharedRecordSerializer)
    def partial_update(self, request, *args, **kwargs):
        market_record_id = kwargs["pk"]
        serializer = self.serializer_class(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        existing_records = self.market_client.get_template_detail(market_record_id)
        existing_template_ids = set([template["id"] for template in json.loads(existing_records["data"]["templates"])])
        data = self._build_template_data(serializer, market_record_id=market_record_id)
        response_data = self.market_client.patch_market_template_record(data, market_record_id)
        if not response_data.get("result"):
            return Response(
                {
                    "result": False,
                    "message": "Failed to update market template record",
                    "code": err_code.OPERATION_FAIL.code,
                }
            )
        TemplateSharedRecord.objects.update_shared_record(
            project_id=int(serializer.validated_data["project_id"]),
            new_template_ids=serializer.validated_data["template_ids"],
            market_record_id=market_record_id,
            creator=serializer.validated_data["creator"],
            existing_template_ids=existing_template_ids,
        )
        return Response({"result": True, "data": response_data, "code": err_code.SUCCESS.code})
