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
from gcloud.contrib.audit.utils import bk_audit_add_event
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
    TemplateLabelQuerySerializer,
)
from gcloud.core.apis.drf.viewsets.base import GcloudModelViewSet
from gcloud.iam_auth import IAMMeta, res_factory
from gcloud.label.models import Label, TemplateLabelRelation
from gcloud.taskflow3.models import TaskConfig, TaskTemplate
from gcloud.tasktmpl3.signals import post_template_save_commit
from gcloud.template_base.domains.template_manager import TemplateManager
from gcloud.user_custom_config.constants import TASKTMPL_ORDERBY_OPTIONS
from gcloud.utils.webhook import apply_webhook_configs, get_webhook_configs, clear_scope_webhooks
from gcloud.constants import WebhookScopeType

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
        "partial_update": IamPermissionInfo(
            IAMMeta.FLOW_EDIT_ACTION, res_factory.resources_for_flow_obj, HAS_OBJECT_PERMISSION
        ),
        "create": IamPermissionInfo(IAMMeta.FLOW_CREATE_ACTION, res_factory.resources_for_project, id_field="project"),
        "enable_independent_subprocess": IamPermissionInfo(
            IAMMeta.PROJECT_VIEW_ACTION, res_factory.resources_for_project, id_field="project_id"
        ),
        "common_info": IamPermissionInfo(
            IAMMeta.PROJECT_VIEW_ACTION, res_factory.resources_for_project, id_field="project__id"
        ),
        "update_template_labels": IamPermissionInfo(
            IAMMeta.FLOW_EDIT_ACTION, res_factory.resources_for_flow_obj, HAS_OBJECT_PERMISSION
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
            "executor_proxy": ["exact"],
        }
        property_fields = [("subprocess_has_update", BooleanPropertyFilter, ["exact"])]

    def filter_by_label_ids(self, query, name, value):
        label_ids = [int(label_id) for label_id in value.strip().split("|")]
        template_ids = list(
            TemplateLabelRelation.objects.filter(label_id__in=label_ids).values_list("template_id", flat=True)
        )
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
        if self.action in ["list", "list_with_top_collection"]:
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
        webhook_configs = get_webhook_configs(scope_code=template_ids)
        templates_labels = TemplateLabelRelation.objects.fetch_templates_labels(template_ids)
        for obj in data:
            obj["is_add"] = 1 if obj["id"] in collected_templates else 0
            obj["template_labels"] = templates_labels.get(obj["id"], [])
            obj["webhook_configs"] = webhook_configs.get(str(obj["id"]), {})
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
        webhook_configs = get_webhook_configs(scope_code=template_ids)
        templates_labels = TemplateLabelRelation.objects.fetch_templates_labels(template_ids)
        for obj in data:
            obj["template_labels"] = templates_labels.get(obj["id"], [])
            obj["is_collected"] = 1 if obj["id"] in collection_template_ids else 0
            obj["collection_id"] = collection_template_map.get(obj["id"], -1)
            obj["webhook_configs"] = webhook_configs.get(str(obj["id"]), {})
        return self.get_paginated_response(data) if page is not None else Response(data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = self.injection_auth_actions(request, serializer.data, instance)
        labels = TemplateLabelRelation.objects.fetch_templates_labels([instance.id]).get(instance.id, [])
        data["template_labels"] = [label["label_id"] for label in labels]
        webhook_configs = get_webhook_configs(scope_code=[str(instance.id)])
        data["webhook_configs"] = webhook_configs.get(str(instance.id), {})
        bk_audit_add_event(
            username=request.user.username,
            action_id=IAMMeta.FLOW_VIEW_ACTION,
            resource_id=IAMMeta.FLOW_RESOURCE,
            instance=instance,
        )
        return Response(data)

    def create(self, request, *args, **kwargs):
        serializer = CreateTaskTemplateSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        name = serializer.validated_data.pop("name")
        creator = request.user.username
        pipeline_tree = json.loads(serializer.validated_data.pop("pipeline_tree"))
        description = serializer.validated_data.pop("description", "")
        webhook_configs = serializer.validated_data.pop("webhook_configs", {})
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
            if webhook_configs:
                apply_result = apply_webhook_configs(webhook_configs, str(serializer.instance.id))
                if not apply_result["result"]:
                    message = apply_result["message"]
                    logger.error(message)
                    return Response(
                        {"detail": ErrorDetail(message, err_code.REQUEST_PARAM_INVALID.code)}, exception=True
                    )
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
        bk_audit_add_event(
            username=request.user.username,
            action_id=IAMMeta.FLOW_CREATE_ACTION,
            resource_id=IAMMeta.FLOW_RESOURCE,
            instance=serializer.instance,
        )
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        template = self.get_object()
        serializer = CreateTaskTemplateSerializer(
            template, data=request.data, partial=partial, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        # update pipeline_template
        name = serializer.validated_data.pop("name")
        editor = request.user.username
        pipeline_tree = json.loads(serializer.validated_data.pop("pipeline_tree"))
        description = serializer.validated_data.pop("description", "")
        webhook_config = serializer.validated_data.pop("webhook_config", {})
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
            if webhook_config:
                apply_result = apply_webhook_configs(webhook_config, str(serializer.instance.id))
                if not apply_result["result"]:
                    message = apply_result["message"]
                    logger.error(message)
                    return Response(
                        {"detail": ErrorDetail(message, err_code.REQUEST_PARAM_INVALID.code)}, exception=True
                    )
            elif not webhook_config and get_webhook_configs([str(serializer.instance.id)]):
                clear_scope_webhooks(WebhookScopeType.TEMPLATE.value, [str(serializer.instance.id)])

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
        bk_audit_add_event(
            username=request.user.username,
            action_id=IAMMeta.FLOW_EDIT_ACTION,
            resource_id=IAMMeta.FLOW_RESOURCE,
            instance=template,
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
        clear_result = clear_scope_webhooks(WebhookScopeType.TEMPLATE.value, [template.id])
        if not clear_result["result"]:
            message = clear_result["message"]
            logger.error(message)
            return Response({"detail": ErrorDetail(message, err_code.REQUEST_PARAM_INVALID.code)}, exception=True)
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
        bk_audit_add_event(
            username=request.user.username,
            action_id=IAMMeta.FLOW_DELETE_ACTION,
            resource_id=IAMMeta.FLOW_RESOURCE,
            instance=template,
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

    @swagger_auto_schema(method="POST", operation_summary="修改流程模板标签", request_body=TemplateLabelQuerySerializer)
    @action(methods=["POST"], detail=True)
    def update_template_labels(self, request, *args, **kwargs):
        label_ids = request.data.get("label_ids")
        template = self.get_object()
        try:
            self._sync_template_lables(template.id, label_ids)
        except Exception as e:
            message = str(e)
            return Response({"detail": ErrorDetail(message, err_code.REQUEST_PARAM_INVALID.code)}, exception=True)

        return Response({"name": template.name, "label_ids": label_ids})
