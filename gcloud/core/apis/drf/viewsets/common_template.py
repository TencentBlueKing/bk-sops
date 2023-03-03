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

import ujson as json
from django.db import transaction
from django.db.models import ExpressionWrapper, Q, BooleanField
from drf_yasg.utils import swagger_auto_schema
from iam import Request, Subject, Action, Resource
from rest_framework.decorators import action
from rest_framework.exceptions import ErrorDetail
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination

from gcloud import err_code
from gcloud.contrib.collection.models import Collection
from gcloud.contrib.operate_record.signal import operate_record_signal
from gcloud.contrib.operate_record.constants import RecordType, OperateType, OperateSource
from gcloud.core.apis.drf.viewsets.base import GcloudModelViewSet
from gcloud.core.apis.drf.serilaziers.common_template import (
    CommonTemplateListSerializer,
    CommonTemplateSerializer,
    CreateCommonTemplateSerializer,
    TopCollectionCommonTemplateSerializer,
)
from gcloud.common_template.signals import post_template_save_commit
from gcloud.common_template.models import CommonTemplate
from gcloud.core.apis.drf.resource_helpers import ViewSetResourceHelper
from gcloud.taskflow3.models import TaskConfig
from gcloud.template_base.domains.template_manager import TemplateManager
from gcloud.iam_auth import res_factory, get_iam_client
from gcloud.iam_auth import IAMMeta
from gcloud.core.apis.drf.filtersets import PropertyFilterSet
from gcloud.core.apis.drf.filters import BooleanPropertyFilter
from gcloud.core.apis.drf.permission import HAS_OBJECT_PERMISSION, IamPermission, IamPermissionInfo
from pipeline.models import TemplateScheme

logger = logging.getLogger("root")
manager = TemplateManager(template_model_cls=CommonTemplate)


class CommonTemplatePermission(IamPermission):
    actions = {
        "list": IamPermissionInfo(pass_all=True),
        "list_with_top_collection": IamPermissionInfo(pass_all=True),
        "retrieve": IamPermissionInfo(
            IAMMeta.COMMON_FLOW_VIEW_ACTION, res_factory.resources_for_common_flow_obj, HAS_OBJECT_PERMISSION
        ),
        "destroy": IamPermissionInfo(
            IAMMeta.COMMON_FLOW_DELETE_ACTION, res_factory.resources_for_common_flow_obj, HAS_OBJECT_PERMISSION
        ),
        "update": IamPermissionInfo(
            IAMMeta.COMMON_FLOW_EDIT_ACTION, res_factory.resources_for_common_flow_obj, HAS_OBJECT_PERMISSION
        ),
        "create": IamPermissionInfo(IAMMeta.COMMON_FLOW_CREATE_ACTION),
        "enable_independent_subprocess": IamPermissionInfo(pass_all=True),
        "common_info": IamPermissionInfo(pass_all=True),
    }


class CommonTemplateFilter(PropertyFilterSet):
    class Meta:
        model = CommonTemplate
        fields = {
            "id": ["exact", "in"],
            "pipeline_template__name": ["icontains"],
            "pipeline_template__creator": ["exact"],
            "pipeline_template__editor": ["exact"],
            "category": ["exact"],
            "pipeline_template__has_subprocess": ["exact"],
            "pipeline_template__edit_time": ["gte", "lte"],
            "pipeline_template__create_time": ["gte", "lte"],
        }
        property_fields = [("subprocess_has_update", BooleanPropertyFilter, ["exact"])]


class CommonTemplateViewSet(GcloudModelViewSet):
    queryset = CommonTemplate.objects.filter(pipeline_template__isnull=False, is_deleted=False)
    pagination_class = LimitOffsetPagination
    iam_resource_helper = ViewSetResourceHelper(
        resource_func=res_factory.resources_for_common_flow_obj,
        actions=[IAMMeta.COMMON_FLOW_VIEW_ACTION, IAMMeta.COMMON_FLOW_EDIT_ACTION, IAMMeta.COMMON_FLOW_DELETE_ACTION],
    )
    filterset_class = CommonTemplateFilter
    permission_classes = [permissions.IsAuthenticated, CommonTemplatePermission]
    ordering = ["-id"]

    def get_serializer_class(self):
        if self.action == "list":
            return CommonTemplateListSerializer
        return CommonTemplateSerializer

    @swagger_auto_schema(
        method="GET", operation_summary="带收藏指定的流程列表", responses={200: TopCollectionCommonTemplateSerializer}
    )
    @action(methods=["GET"], detail=False)
    def list_with_top_collection(self, request, *args, **kwargs):
        order_by = request.query_params.get("order_by") or "-id"
        orderings = ("-is_collected", order_by)

        collection_templates = Collection.objects.filter(
            category="common_flow", username=request.user.username
        ).values_list("instance_id", "id")
        collection_template_ids = [instance_id for instance_id, _ in collection_templates]
        collection_id_template_id_map = {
            instance_id: collection_id for instance_id, collection_id in collection_templates
        }

        queryset = (
            self.filter_queryset(self.get_queryset())
            .annotate(is_collected=ExpressionWrapper(Q(id__in=collection_template_ids), output_field=BooleanField()))
            .order_by(*orderings)
        )
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page if page is not None else queryset, many=True)
        # 注入权限
        data = self.injection_auth_actions(request, serializer.data, serializer.instance)

        # 注入公共流程新建任务权限
        templates = self._inject_project_based_task_create_action(request, [template["id"] for template in data])

        for obj in data:
            obj["is_collected"] = 1 if obj["id"] in collection_template_ids else 0
            obj["collection_id"] = collection_id_template_id_map.get(obj["id"], -1)
            if obj["id"] in templates:
                obj["auth_actions"].append(IAMMeta.COMMON_FLOW_CREATE_TASK_ACTION)
        return self.get_paginated_response(data) if page is not None else Response(data)

    @staticmethod
    def _inject_project_based_task_create_action(request, common_template_ids):
        project_id = request.query_params.get("project__id")
        if not project_id:
            return []
        iam = get_iam_client()
        system = IAMMeta.SYSTEM_ID

        allowed_template_ids = []
        for template_id in common_template_ids:
            resource = [
                Resource(system, IAMMeta.COMMON_FLOW_RESOURCE, str(template_id), {}),
                Resource(system, IAMMeta.PROJECT_RESOURCE, str(project_id), {}),
            ]
            try:
                is_allow = iam.is_allowed(
                    Request(
                        system=system,
                        subject=Subject("user", request.user.username),
                        action=Action(IAMMeta.COMMON_FLOW_CREATE_TASK_ACTION),
                        resources=resource,
                        environment=None,
                    )
                )
            except Exception as e:
                logger.exception(f"[iam_is_allowed]: {e}")
                is_allow = False
            if is_allow:
                allowed_template_ids.append(template_id)

        return allowed_template_ids

    def create(self, request, *args, **kwargs):
        serializer = CreateCommonTemplateSerializer(data=request.data)
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
                message = result["message"]
                logger.error(message)
                return Response({"detail": ErrorDetail(message, err_code.REQUEST_PARAM_INVALID.code)}, exception=True)

            serializer.validated_data["pipeline_template"] = result["data"]

            self.perform_create(serializer)
        # 发送信号
        post_template_save_commit.send(sender=CommonTemplate, template_id=serializer.instance.id, is_deleted=False)
        # 注入权限
        data = self.injection_auth_actions(request, serializer.data, serializer.instance)
        # 记录操作流水
        operate_record_signal.send(
            sender=RecordType.common_template.name,
            operator=creator,
            operate_type=OperateType.create.name,
            operate_source=OperateSource.common.name,
            instance_id=serializer.instance.id,
        )
        headers = self.get_success_headers(serializer.data)
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        template = self.get_object()
        serializer = CreateCommonTemplateSerializer(template, data=request.data, partial=partial)
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
                message = result["message"]
                logger.error(message)
                return Response({"detail": ErrorDetail(message, err_code.REQUEST_PARAM_INVALID.code)}, exception=True)

            serializer.validated_data["pipeline_template"] = template.pipeline_template
            self.perform_update(serializer)
        # 发送信号
        post_template_save_commit.send(sender=CommonTemplate, template_id=serializer.instance.id, is_deleted=False)
        # 注入权限
        data = self.injection_auth_actions(request, serializer.data, template)
        # 记录操作流水
        operate_record_signal.send(
            sender=RecordType.common_template.name,
            operator=editor,
            operate_type=OperateType.update.name,
            operate_source=OperateSource.common.name,
            instance_id=serializer.instance.id,
        )
        return Response(data)

    def destroy(self, request, *args, **kwargs):
        template = self.get_object()
        can_delete, message = manager.can_delete(template)
        if not can_delete:
            return Response({"detail": ErrorDetail(message, err_code.REQUEST_PARAM_INVALID.code)}, exception=True)
        # 发送信号
        post_template_save_commit.send(sender=CommonTemplate, template_id=template.id, is_deleted=True)
        # 删除流程模板
        self.perform_destroy(template)
        # 记录操作流水
        operate_record_signal.send(
            sender=RecordType.common_template.name,
            operator=request.user.username,
            operate_type=OperateType.delete.name,
            operate_source=OperateSource.common.name,
            instance_id=template.id,
        )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(method="GET", operation_summary="查询流程是否开启独立子流程")
    @action(methods=["GET"], detail=True)
    def enable_independent_subprocess(self, request, *args, **kwargs):
        template_id = kwargs.get("pk")
        project_id = -1
        independent_subprocess_enable = TaskConfig.objects.enable_independent_subprocess(project_id, template_id)
        return Response({"enable": independent_subprocess_enable})

    @swagger_auto_schema(method="GET", operation_summary="获取流程详情公开信息")
    @action(methods=["GET"], detail=True)
    def common_info(self, request, *args, **kwargs):
        template = self.get_object()
        schemes = TemplateScheme.objects.filter(template=template.pipeline_template).values_list("id", "name")
        schemes_info = [{"id": scheme_id, "name": scheme_name} for scheme_id, scheme_name in schemes]
        return Response({"name": template.name, "schemes": schemes_info})
