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

from django.db.models import BooleanField, ExpressionWrapper, Q
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.exceptions import ErrorDetail
from rest_framework import status, permissions
from django.contrib.auth import get_user_model
from django.db import transaction
from django_filters import CharFilter

from gcloud import err_code
from pipeline.models import TemplateRelationship

from gcloud.contrib.collection.models import Collection
from gcloud.core.apis.drf.viewsets.base import GcloudModelViewSet
from gcloud.label.models import TemplateLabelRelation, Label
from gcloud.tasktmpl3.signals import post_template_save_commit
from gcloud.taskflow3.models import TaskTemplate
from gcloud.core.apis.drf.serilaziers.task_template import (
    TaskTemplateListSerializer,
    TaskTemplateSerializer,
    CreateTaskTemplateSerializer,
    TopCollectionTaskTemplateSerializer,
)
from gcloud.core.apis.drf.resource_helpers import ViewSetResourceHelper
from gcloud.iam_auth import res_factory
from gcloud.iam_auth import IAMMeta
from gcloud.template_base.domains.template_manager import TemplateManager
from gcloud.core.apis.drf.filtersets import PropertyFilterSet
from gcloud.core.apis.drf.filters import BooleanPropertyFilter
from gcloud.contrib.operate_record.signal import operate_record_signal
from gcloud.contrib.operate_record.constants import OperateType, OperateSource, RecordType
from gcloud.core.apis.drf.permission import HAS_OBJECT_PERMISSION, IamPermission, IamPermissionInfo
from gcloud.user_custom_config.constants import TASKTMPL_ORDERBY_OPTIONS


logger = logging.getLogger("root")
manager = TemplateManager(template_model_cls=TaskTemplate)


class TaskTemplatePermission(IamPermission):
    actions = {
        "list": IamPermissionInfo(
            IAMMeta.PROJECT_VIEW_ACTION, res_factory.resources_for_project, id_field="project__id"
        ),
        "list_with_top_collection": IamPermissionInfo(
            IAMMeta.PROJECT_VIEW_ACTION, res_factory.resources_for_project, id_field="project__id"
        ),
        "retrieve": IamPermissionInfo(
            IAMMeta.FLOW_VIEW_ACTION, res_factory.resources_for_flow_obj, HAS_OBJECT_PERMISSION
        ),
        "destroy": IamPermissionInfo(
            IAMMeta.FLOW_DELETE_ACTION, res_factory.resources_for_flow_obj, HAS_OBJECT_PERMISSION
        ),
        "update": IamPermissionInfo(
            IAMMeta.FLOW_EDIT_ACTION, res_factory.resources_for_flow_obj, HAS_OBJECT_PERMISSION
        ),
        "create": IamPermissionInfo(IAMMeta.FLOW_CREATE_ACTION, res_factory.resources_for_project, id_field="project"),
    }


class TaskTemplateFilter(PropertyFilterSet):
    label_ids = CharFilter(method="filter_by_label_ids")

    class Meta:
        model = TaskTemplate
        fields = {
            "id": ["exact"],
            "pipeline_template__name": ["icontains"],
            "pipeline_template__creator": ["contains"],
            "category": ["exact"],
            "pipeline_template__has_subprocess": ["exact"],
            "pipeline_template__edit_time": ["gte", "lte"],
            "pipeline_template__create_time": ["gte", "lte"],
            "project__id": ["exact"],
        }
        property_fields = [("subprocess_has_update", BooleanPropertyFilter, ["exact"])]

    def filter_by_label_ids(self, query, name, value):
        label_ids = [int(label_id) for label_id in value.strip().split(",")]
        template_ids = list(TemplateLabelRelation.objects.fetch_template_ids_using_union_labels(label_ids))
        condition = {"id__in": template_ids}
        return query.filter(**condition)


class TaskTemplateViewSet(GcloudModelViewSet):
    queryset = TaskTemplate.objects.filter(pipeline_template__isnull=False, is_deleted=False)
    pagination_class = LimitOffsetPagination
    filterset_class = TaskTemplateFilter
    permission_classes = [permissions.IsAuthenticated, TaskTemplatePermission]
    iam_resource_helper = ViewSetResourceHelper(
        resource_func=res_factory.resources_for_flow_obj,
        actions=[
            IAMMeta.FLOW_VIEW_ACTION,
            IAMMeta.FLOW_EDIT_ACTION,
            IAMMeta.FLOW_DELETE_ACTION,
            IAMMeta.FLOW_CREATE_TASK_ACTION,
            IAMMeta.FLOW_CREATE_CLOCKED_TASK_ACTION,
            IAMMeta.FLOW_CREATE_MINI_APP_ACTION,
            IAMMeta.FLOW_CREATE_PERIODIC_TASK_ACTION,
        ],
    )
    ordering_fields = ["pipeline_template"] + [order["value"] for order in TASKTMPL_ORDERBY_OPTIONS]

    def get_serializer_class(self):
        if self.action == "list":
            return TaskTemplateListSerializer
        return TaskTemplateSerializer

    def _sync_template_lables(self, template_id, label_ids):
        """
        创建或更新模板时同步模板标签数据
        """
        if label_ids:
            label_ids = list(set(label_ids))
            if not Label.objects.check_label_ids(label_ids):
                message = "Containing template label not exist, please check."
                return Response({"detail": ErrorDetail(message, err_code.REQUEST_PARAM_INVALID.code)}, exception=True)
            try:
                TemplateLabelRelation.objects.set_labels_for_template(template_id, label_ids)
            except Exception as e:
                return Response({"detail": ErrorDetail(str(e), err_code.REQUEST_PARAM_INVALID.code)}, exception=True)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page if page is not None else queryset, many=True)
        # 注入权限
        data = self.injection_auth_actions(request, serializer.data, serializer.instance)
        user_model = get_user_model()
        collected_templates = (
            user_model.objects.get(username=request.user.username).tasktemplate_set.all().values_list("id", flat=True)
        )
        template_ids = [obj["id"] for obj in data]
        templates_labels = TemplateLabelRelation.objects.fetch_templates_labels(template_ids)
        for obj in data:
            obj["is_add"] = 1 if obj["id"] in collected_templates else 0
            obj["template_labels"] = templates_labels.get(obj["id"], [])
        return self.get_paginated_response(data) if page is not None else Response(data)

    @swagger_auto_schema(
        method="GET", operation_summary="带收藏指定的流程列表", responses={200: TopCollectionTaskTemplateSerializer}
    )
    @action(methods=["GET"], detail=False)
    def list_with_top_collection(self, request, *args, **kwargs):
        project_id = int(request.query_params["project__id"])
        order_by = request.query_params.get("order_by") or "-id"
        orderings = ("-is_collected", order_by)

        user_collections = Collection.objects.filter(category="flow", username=request.user.username).values()
        # 取出用户在当前项目的收藏id
        collection_template_ids = []
        collection_id_template_id_map = {}
        for user_collection in user_collections:
            extra_info = json.loads(user_collection["extra_info"])
            if int(extra_info["project_id"]) == project_id:
                instance_id = user_collection["instance_id"]
                collection_template_ids.append(instance_id)
                collection_id_template_id_map[instance_id] = user_collection["id"]

        queryset = (
            self.filter_queryset(self.get_queryset())
            .annotate(is_collected=ExpressionWrapper(Q(id__in=collection_template_ids), output_field=BooleanField()))
            .order_by(*orderings)
        )
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page if page is not None else queryset, many=True)
        # 注入权限
        data = self.injection_auth_actions(request, serializer.data, serializer.instance)
        template_ids = [obj["id"] for obj in data]
        templates_labels = TemplateLabelRelation.objects.fetch_templates_labels(template_ids)
        for obj in data:
            obj["template_labels"] = templates_labels.get(obj["id"], [])
            obj["is_collected"] = 1 if obj["id"] in collection_template_ids else 0
            obj["collection_id"] = collection_id_template_id_map.get(obj["id"], -1)
        return self.get_paginated_response(data) if page is not None else Response(data)

    def create(self, request, *args, **kwargs):
        serializer = CreateTaskTemplateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        name = serializer.validated_data.pop("name")
        creator = request.user.username
        pipeline_tree = json.loads(serializer.validated_data.pop("pipeline_tree"))
        description = serializer.validated_data.pop("description", "")
        with transaction.atomic():
            result = manager.create_pipeline(
                name=name, creator=creator, pipeline_tree=pipeline_tree, description=description
            )

            if not result["result"]:
                message = result["message"]
                logger.error(message)
                return Response({"detail": ErrorDetail(message, err_code.REQUEST_PARAM_INVALID.code)}, exception=True)

            serializer.validated_data["pipeline_template_id"] = result["data"].template_id
            template_labels = serializer.validated_data.pop("template_labels")
            self.perform_create(serializer)
            self._sync_template_lables(serializer.instance.id, template_labels)
            headers = self.get_success_headers(serializer.data)
        # 发送信号
        post_template_save_commit.send(
            sender=TaskTemplate,
            project_id=serializer.instance.project_id,
            template_id=serializer.instance.id,
            is_deleted=False,
        )
        # 注入权限
        data = self.injection_auth_actions(request, serializer.data, serializer.instance)
        # 记录操作流水
        operate_record_signal.send(
            sender=RecordType.template.name,
            operator=creator,
            operate_type=OperateType.create.name,
            operate_source=OperateSource.project.name,
            instance_id=serializer.instance.id,
            project_id=serializer.instance.project.id,
        )
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        template = self.get_object()
        serializer = CreateTaskTemplateSerializer(template, data=request.data, partial=partial)
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
            template_labels = serializer.validated_data.pop("template_labels")
            self.perform_update(serializer)
            self._sync_template_lables(serializer.instance.id, template_labels)
        # 发送信号
        post_template_save_commit.send(
            sender=TaskTemplate,
            project_id=serializer.instance.project_id,
            template_id=serializer.instance.id,
            is_deleted=serializer.instance.is_deleted,
        )
        # 注入权限
        data = self.injection_auth_actions(request, serializer.data, template)
        # 记录操作流水
        operate_record_signal.send(
            sender=RecordType.template.name,
            operator=editor,
            operate_type=OperateType.update.name,
            operate_source=OperateSource.project.name,
            instance_id=serializer.instance.id,
            project_id=serializer.instance.project.id,
        )
        return Response(data)

    def destroy(self, request, *args, **kwargs):
        template = self.get_object()
        manager = TemplateManager(TaskTemplate)
        can_delete, message = manager.can_delete(template)
        if not can_delete:
            return Response({"detail": ErrorDetail(message, err_code.REQUEST_PARAM_INVALID.code)}, exception=True)
        # 删除流程模板引用的子流程节点的执行方案
        pipeline_template_id = template.pipeline_template.template_id
        relation_queryset = TemplateRelationship.objects.filter(ancestor_template_id=pipeline_template_id)
        for relation in relation_queryset:
            relation.templatescheme_set.clear()
        # 删除流程模板
        template.is_deleted = True
        template.save()
        # 发送信号
        post_template_save_commit.send(
            sender=TaskTemplate, project_id=template.project_id, template_id=template.id, is_deleted=template.is_deleted
        )
        # 记录操作流水
        operate_record_signal.send(
            sender=RecordType.template.name,
            operator=request.user.username,
            operate_type=OperateType.delete.name,
            operate_source=OperateSource.project.name,
            instance_id=template.id,
            project_id=template.project.id,
        )
        return Response(status=status.HTTP_204_NO_CONTENT)
