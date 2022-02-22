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
import ujson as json
from django.db import transaction
from rest_framework.exceptions import ErrorDetail
from rest_framework import status
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination

from gcloud import err_code
from gcloud.contrib.operate_record.decorators import record_operation
from gcloud.contrib.operate_record.constants import RecordType, OperateType, OperateSource
from gcloud.core.apis.drf.viewsets.base import GcloudModelViewSet
from gcloud.core.apis.drf.serilaziers.common_template import CommonTemplateSerializer, CreateCommonTemplateSerializer
from gcloud.common_template.models import CommonTemplate
from gcloud.core.apis.drf.resource_helpers import ViewSetResourceHelper
from gcloud.template_base.domains.template_manager import TemplateManager
from gcloud.iam_auth import res_factory
from gcloud.iam_auth.conf import COMMON_FLOW_ACTIONS
from ..filtersets import PropertyFilterSet
from ..filters import BooleanPropertyFilter

logger = logging.getLogger("root")
manager = TemplateManager(template_model_cls=CommonTemplate)


class CommonTemplateFilter(PropertyFilterSet):
    class Meta:
        model = CommonTemplate
        fields = {
            "id": ["exact"],
            "pipeline_template__name": ["icontains"],
            "pipeline_template__creator": ["contains"],
            "category": ["exact"],
            "pipeline_template__has_subprocess": ["exact"],
            "pipeline_template__edit_time": ["gte", "lte"],
            "pipeline_template__create_time": ["gte", "lte"],
        }
        property_fields = [("subprocess_has_update", BooleanPropertyFilter, ["exact"])]


class CommonTemplateViewSet(GcloudModelViewSet):
    queryset = CommonTemplate.objects.filter(pipeline_template__isnull=False, is_deleted=False)
    pagination_class = LimitOffsetPagination
    serializer_class = CommonTemplateSerializer
    create_serializer_class = CreateCommonTemplateSerializer
    iam_resource_helper = ViewSetResourceHelper(
        resource_func=res_factory.resources_for_common_flow_obj, actions=COMMON_FLOW_ACTIONS
    )
    filterset_class = CommonTemplateFilter

    @record_operation(RecordType.common_template.name, OperateType.create.name, OperateSource.common.name)
    def create(self, request, *args, **kwargs):
        serializer = self.create_serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            name = serializer.validated_data.pop("name")
            creator = request.user.username
            pipeline_tree = json.loads(serializer.validated_data.pop("pipeline_tree"))
            description = serializer.validated_data.pop("description", "")
        except (KeyError, ValueError) as e:
            message = str(e)
            return Response({"detail": ErrorDetail(message, err_code.REQUEST_PARAM_INVALID.code)}, exception=True)
        with transaction.atomic():
            result = manager.create_pipeline(
                name=name, creator=creator, pipeline_tree=pipeline_tree, description=description
            )

            if not result["result"]:
                message = result["verbose_message"]
                logger.error(message)
                return Response({"detail": ErrorDetail(message, err_code.REQUEST_PARAM_INVALID.code)}, exception=True)

            serializer.validated_data["pipeline_template"] = result["data"]

            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @record_operation(RecordType.common_template.name, OperateType.update.name, OperateSource.common.name)
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        template = self.get_object()
        serializer = self.create_serializer_class(template, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        # update pipeline_template
        name = serializer.validated_data.pop("name")
        editor = request.user.username
        pipeline_tree = json.loads(serializer.validated_data.pop("pipeline_tree"))
        description = serializer.validated_data.pop("description", "")
        with transaction.atomic():
            result = manager.update_pipeline(
                pipeline_template=template.pipeline_template,
                editor=editor,
                name=name,
                pipeline_tree=pipeline_tree,
                description=description,
            )

            if not result["result"]:
                message = result["verbose_message"]
                logger.error(message)
                return Response({"detail": ErrorDetail(message, err_code.REQUEST_PARAM_INVALID.code)}, exception=True)

            serializer.validated_data["pipeline_template"] = template.pipeline_template
            self.perform_update(serializer)
            # 注入权限
            data = self.injection_auth_actions(request, serializer.data, template)
            return Response(data)

    @record_operation(RecordType.common_template.name, OperateType.delete.name, OperateSource.common.name)
    def destroy(self, request, *args, **kwargs):
        template = self.get_object()
        can_delete, message = manager.can_delete(template)
        if not can_delete:
            return Response({"detail": ErrorDetail(message, err_code.REQUEST_PARAM_INVALID.code)}, exception=True)
        self.perform_destroy(template)
        return Response(status=status.HTTP_204_NO_CONTENT)
