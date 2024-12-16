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
from rest_framework.decorators import action
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


class TemplateSceneViewSet(viewsets.ViewSet):
    queryset = TemplateSharedRecord.objects.all()
    serializer_class = TemplateSharedRecordSerializer
    permission_classes = [permissions.IsAuthenticated, SharedTemplateRecordPermission]

    market_client = MarketAPIClient()

    def _build_template_data(self, serializer, **kwargs):
        templates = TaskTemplate.objects.filter(id__in=serializer.validated_data["template_ids"], is_deleted=False)
        template_info = [{"id": template.id, "name": template.name} for template in templates]
        data = {"source_system": settings.APP_CODE, "templates": json.dumps(template_info), **serializer.validated_data}
        market_record_id = kwargs.get("market_record_id")
        if market_record_id:
            data["id"] = market_record_id
        return data

    def _handle_response(self, response_data, error_message):
        if not response_data.get("result"):
            logging.exception(error_message)
            return Response(
                {
                    "result": False,
                    "message": error_message,
                    "code": err_code.OPERATION_FAIL.code,
                }
            )
        return None

    @action(detail=False, methods=["get"])
    def get_service_category(self, request, *args, **kwargs):
        response_data = self.market_client.get_service_category()
        error_response = self._handle_response(response_data, "Failed to obtain scene category")
        if error_response:
            return error_response
        return Response({"result": True, "data": response_data["data"], "code": err_code.SUCCESS.code})

    @action(detail=False, methods=["get"])
    def get_scene_label(self, request, *args, **kwargs):
        response_data = self.market_client.get_scene_label()
        error_response = self._handle_response(response_data, "Failed to obtain scene tag list")
        if error_response:
            return error_response
        return Response({"result": True, "data": response_data["data"], "code": err_code.SUCCESS.code})

    @action(detail=False, methods=["get"])
    def get_risk_level(self, request, *args, **kwargs):
        response_data = self.market_client.get_risk_level()
        error_response = self._handle_response(response_data, "Failed to obtain the market risk level list")
        if error_response:
            return error_response
        return Response({"result": True, "data": response_data["data"], "code": err_code.SUCCESS.code})

    def list(self, request, *args, **kwargs):
        response_data = self.market_client.get_template_scene_list()
        error_response = self._handle_response(response_data, "Failed to obtain the market template list")
        if error_response:
            return error_response
        return Response({"result": True, "data": response_data, "code": err_code.SUCCESS.code})

    @swagger_auto_schema(request_body=TemplateSharedRecordSerializer)
    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = self._build_template_data(serializer)
        response_data = self.market_client.create_template_scene(data)
        error_response = self._handle_response(response_data, "Failed to create market template record")
        if error_response:
            return error_response

        TemplateSharedRecord.objects.update_shared_record(
            project_id=int(serializer.validated_data["project_code"]),
            new_template_ids=serializer.validated_data["template_ids"],
            market_record_id=response_data["data"]["id"],
            creator=request.user.username,
        )
        return Response({"result": True, "data": response_data, "code": err_code.SUCCESS.code})

    @swagger_auto_schema(request_body=TemplateSharedRecordSerializer)
    def partial_update(self, request, *args, **kwargs):
        market_record_id = kwargs["pk"]
        serializer = self.serializer_class(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        existing_records = self.market_client.get_template_scene_detail(market_record_id)
        existing_market_template_ids = set(
            [template["id"] for template in json.loads(existing_records["data"]["templates"])]
        )

        data = self._build_template_data(serializer, market_record_id=market_record_id)
        response_data = self.market_client.patch_template_scene(data, market_record_id)
        error_response = self._handle_response(response_data, "Failed to update market template record")
        if error_response:
            return error_response

        TemplateSharedRecord.objects.update_shared_record(
            project_id=int(serializer.validated_data["project_code"]),
            new_template_ids=serializer.validated_data["template_ids"],
            market_record_id=market_record_id,
            creator=request.user.username,
            existing_market_template_ids=existing_market_template_ids,
        )
        return Response({"result": True, "data": response_data, "code": err_code.SUCCESS.code})
