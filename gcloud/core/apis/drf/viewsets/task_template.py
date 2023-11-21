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

from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import BooleanField, ExpressionWrapper, Q
from django.utils.translation import ugettext_lazy as _
from django_filters import CharFilter
from drf_yasg.utils import swagger_auto_schema
from pipeline.models import TemplateRelationship, TemplateScheme
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.exceptions import ErrorDetail
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response

from gcloud import err_code
from gcloud.contrib.collection.models import Collection
from gcloud.contrib.operate_record.constants import OperateSource, OperateType, RecordType
from gcloud.contrib.operate_record.signal import operate_record_signal
from gcloud.core.apis.drf.filters import BooleanPropertyFilter
from gcloud.core.apis.drf.filtersets import PropertyFilterSet
from gcloud.core.apis.drf.permission import HAS_OBJECT_PERMISSION, IamPermission, IamPermissionInfo
from gcloud.core.apis.drf.resource_helpers import ViewSetResourceHelper
from gcloud.core.apis.drf.serilaziers.task_template import (
    CreateTaskTemplateSerializer,
    ProjectFilterQuerySerializer,
    ProjectInfoQuerySerializer,
    TaskTemplateListSerializer,
    TaskTemplateSerializer,
    TopCollectionTaskTemplateSerializer,
    UpdateDraftPipelineTreeSerializer,
    UpdateTaskTemplateSerializer,
)
from gcloud.core.apis.drf.viewsets.base import GcloudModelViewSet
from gcloud.core.apis.drf.viewsets.draft_template import DraftTemplateViewSetMixin
from gcloud.iam_auth import IAMMeta, res_factory
from gcloud.label.models import Label, TemplateLabelRelation
from gcloud.taskflow3.models import TaskConfig, TaskTemplate
from gcloud.tasktmpl3.signals import post_template_save_commit
from gcloud.template_base.domains.template_manager import TemplateManager
from gcloud.user_custom_config.constants import DEFAULT_PIPELINE_TREE, TASKTMPL_ORDERBY_OPTIONS

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
        "draft": IamPermissionInfo(IAMMeta.FLOW_VIEW_ACTION, res_factory.resources_for_flow_obj, HAS_OBJECT_PERMISSION),
        "destroy": IamPermissionInfo(
            IAMMeta.FLOW_DELETE_ACTION, res_factory.resources_for_flow_obj, HAS_OBJECT_PERMISSION
        ),
        "update_draft": IamPermissionInfo(
            IAMMeta.FLOW_EDIT_ACTION, res_factory.resources_for_flow_obj, HAS_OBJECT_PERMISSION
        ),
        "publish_draft": IamPermissionInfo(
            IAMMeta.FLOW_PUBLISH_DRAFT_ACTION, res_factory.resources_for_flow_obj, HAS_OBJECT_PERMISSION
        ),
        "update": IamPermissionInfo(
            IAMMeta.FLOW_EDIT_ACTION, res_factory.resources_for_flow_obj, HAS_OBJECT_PERMISSION
        ),
        "create": IamPermissionInfo(IAMMeta.FLOW_CREATE_ACTION, res_factory.resources_for_project, id_field="project"),
        "enable_independent_subprocess": IamPermissionInfo(
            IAMMeta.PROJECT_VIEW_ACTION, res_factory.resources_for_project, id_field="project_id"
        ),
        "common_info": IamPermissionInfo(
            IAMMeta.PROJECT_VIEW_ACTION, res_factory.resources_for_project, id_field="project__id"
        ),
    }


class TaskTemplateFilter(PropertyFilterSet):
    label_ids = CharFilter(method="filter_by_label_ids")

    class Meta:
        model = TaskTemplate
        fields = {
            "id": ["exact", "in"],
            "pipeline_template__name": ["icontains"],
            "pipeline_template__creator": ["exact"],
            "pipeline_template__editor": ["exact"],
            "category": ["exact"],
            "pipeline_template__has_subprocess": ["exact"],
            "pipeline_template__edit_time": ["gte", "lte"],
            "pipeline_template__create_time": ["gte", "lte"],
            "project__id": ["exact"],
            "published": ["exact"],
        }
        property_fields = [("subprocess_has_update", BooleanPropertyFilter, ["exact"])]

    def filter_by_label_ids(self, query, name, value):
        label_ids = [int(label_id) for label_id in value.strip().split("|")]
        template_ids = list(
            TemplateLabelRelation.objects.filter(label_id__in=label_ids).values_list("template_id", flat=True)
        )
        condition = {"id__in": template_ids}
        return query.filter(**condition)


class TaskTemplateViewSet(GcloudModelViewSet, DraftTemplateViewSetMixin):
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
            IAMMeta.FLOW_PUBLISH_DRAFT_ACTION,
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
        label_ids = list(set(label_ids))
        if not Label.objects.check_label_ids(label_ids):
            message = _("流程保存失败: 流程设置的标签不存在, 请检查配置后重试 | _sync_template_lables")
            logger.error(message)
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
        project_id = request.query_params["project__id"]
        order_by = request.query_params.get("order_by") or "-id"
        orderings = ("-is_collected", order_by)

        # 取出用户在当前项目的收藏id
        collection_template_ids, collection_template_map = Collection.objects.get_user_project_collection_instance_info(
            project_id=project_id, username=request.user.username, category="flow"
        )

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
            obj["collection_id"] = collection_template_map.get(obj["id"], -1)
        return self.get_paginated_response(data) if page is not None else Response(data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = self.injection_auth_actions(request, serializer.data, instance)
        labels = TemplateLabelRelation.objects.fetch_templates_labels([instance.id]).get(instance.id, [])
        data["template_labels"] = [label["label_id"] for label in labels]
        return Response(data)

    def create(self, request, *args, **kwargs):
        serializer = CreateTaskTemplateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        creator = request.user.username
        with transaction.atomic():
            description = serializer.validated_data.pop("description", "")
            name = serializer.validated_data.pop("name", "")
            labels = serializer.validated_data.pop("template_labels", [])
            # 创建一份模板，该模板不会被使用，未发布
            result = manager.create_pipeline(
                name=name, creator=creator, pipeline_tree=DEFAULT_PIPELINE_TREE, description=description
            )

            if not result["result"]:
                message = result["message"]
                logger.error(message)
                return Response({"detail": ErrorDetail(message, err_code.REQUEST_PARAM_INVALID.code)}, exception=True)

            serializer.validated_data["pipeline_template_id"] = result["data"].template_id

            # 创建快照
            pipeline_tree = json.loads(serializer.validated_data.pop("pipeline_tree"))
            draft_template_id = manager.create_draft_without_template(
                pipeline_tree, request.user.username, name, description, labels
            )

            serializer.validated_data["published"] = False
            serializer.validated_data["draft_template_id"] = draft_template_id
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)

        # 发送信号
        post_template_save_commit.send(
            sender=TaskTemplate,
            project_id=serializer.instance.project.id,
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
        serializer = UpdateTaskTemplateSerializer(template, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        # 更新时将只允许更新流程的通知等全局信息
        editor = request.user.username
        with transaction.atomic():
            self.perform_update(serializer)
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

    @swagger_auto_schema(method="GET", operation_summary="查询流程是否开启独立子流程", query_serializer=ProjectInfoQuerySerializer)
    @action(methods=["GET"], detail=True)
    def enable_independent_subprocess(self, request, *args, **kwargs):
        template_id = kwargs.get("pk")
        project_id = request.query_params.get("project_id")
        independent_subprocess_enable = TaskConfig.objects.enable_independent_subprocess(project_id, template_id)
        return Response({"enable": independent_subprocess_enable})

    @swagger_auto_schema(method="GET", operation_summary="获取流程详情公开信息", query_serializer=ProjectFilterQuerySerializer)
    @action(methods=["GET"], detail=True)
    def common_info(self, request, *args, **kwargs):
        template = self.get_object()
        schemes = TemplateScheme.objects.filter(template=template.pipeline_template).values_list("id", "name")
        schemes_info = [{"id": scheme_id, "name": scheme_name} for scheme_id, scheme_name in schemes]
        return Response({"name": template.name, "schemes": schemes_info})

    @swagger_auto_schema(method="GET", operation_summary="获取流程的草稿信息")
    @action(methods=["GET"], detail=True)
    def draft(self, request, *args, **kwargs):
        """
        获取草稿内容
        """
        return Response(self.get_draft(manager, self.get_object(), request.user.username))

    @swagger_auto_schema(method="post", operation_summary="更新流程草稿信息", request_body=UpdateDraftPipelineTreeSerializer)
    @action(methods=["POST"], detail=True)
    def update_draft(self, request, *args, **kwargs):
        """
        更新草稿
        """
        task_template = self.get_object()
        result = self.update_template_draft(manager, task_template, request)
        if not result["result"]:
            message = result["message"]
            logger.error(message)
            return Response({"detail": ErrorDetail(message, err_code.REQUEST_PARAM_INVALID.code)}, exception=True)

        return Response(
            {
                "name": task_template.draft_template.name,
                "template_labels": task_template.draft_template.labels,
                "description": task_template.draft_template.description,
                "editor": task_template.draft_template.editor,
                "pipeline_tree": json.dumps(task_template.draft_pipeline_tree),
                "edit_time": task_template.draft_template.edit_time.strftime("%Y-%m-%d %H:%M:%S"),
            }
        )

    @swagger_auto_schema(method="post", operation_summary="发布该流程")
    @action(methods=["POST"], detail=True)
    def publish_draft(self, request, *args, **kwargs):
        """
        发布草稿
        """
        task_template = self.get_object()
        result = self.publish_template_draft(manager, task_template, request.user.username)
        if not result["result"]:
            message = result["message"]
            logger.error(message)
            return Response({"detail": ErrorDetail(message, err_code.REQUEST_PARAM_INVALID.code)}, exception=True)
        self._sync_template_lables(task_template.id, task_template.draft_template.labels)
        return Response()
