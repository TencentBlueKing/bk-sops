# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
import logging

from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.exceptions import APIException
from rest_framework.response import Response

from gcloud.common_template.models import CommonTemplate
from gcloud.core.apis.drf.viewsets import ApiMixin
from gcloud.tasktmpl3.models import TaskTemplate
from gcloud.template_base.apis.drf.permission import ProjectTemplatePermission, CommonTemplatePermission
from gcloud.template_base.apis.drf.serilaziers.template import TemplateIdsSerializer, BatchDeleteSerialzer
from gcloud.template_base.domains.template_manager import TemplateManager

logger = logging.getLogger("root")


class TemplateViewSet(ApiMixin, viewsets.GenericViewSet):
    template_ids_serializer = TemplateIdsSerializer

    @swagger_auto_schema(method="post", request_body=TemplateIdsSerializer, responses={200: BatchDeleteSerialzer})
    @action(methods=["post"], detail=False)
    def batch_delete(self, request, *args, **kwargs):
        """批量删除流程"""
        data = request.data
        body_serializer = self.template_ids_serializer(data=data)
        body_serializer.is_valid(raise_exception=True)
        template_ids = body_serializer.validated_data.get("template_ids")

        manager = TemplateManager(template_model_cls=self.tmpl_model)
        result = manager.batch_delete(template_ids)
        if not result["result"]:
            raise APIException(f'[batch_delete] result False: {result["message"]}')
        return Response(result["data"])


class ProjectTemplateViewSet(TemplateViewSet):
    queryset = TaskTemplate.objects.all()
    permission_classes = [permissions.IsAuthenticated | ProjectTemplatePermission]
    template_type = "project"
    tmpl_model = TaskTemplate


class CommonTemplateViewSet(TemplateViewSet):
    queryset = CommonTemplate.objects.all()
    permission_classes = [permissions.IsAuthenticated | CommonTemplatePermission]
    template_type = "common"
    tmpl_model = CommonTemplate
