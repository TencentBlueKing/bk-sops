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

from django.db import transaction
from django.db.models import BooleanField, ExpressionWrapper, Q
from django.utils.translation import gettext_lazy as _
from pipeline.exceptions import PipelineException
from rest_framework import permissions, status
from rest_framework.exceptions import APIException
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response

from gcloud import err_code
from gcloud.common_template.models import CommonTemplate
from gcloud.constants import COMMON, PERIOD_TASK_NAME_MAX_LENGTH, PROJECT
from gcloud.contrib.audit.utils import bk_audit_add_event
from gcloud.contrib.collection.models import Collection
from gcloud.core.apis.drf.exceptions import ValidationException
from gcloud.core.apis.drf.filtersets import AllLookupSupportFilterSet
from gcloud.core.apis.drf.permission import (
    HAS_OBJECT_PERMISSION,
    IamPermission,
    IamPermissionInfo,
    IamUserTypeBasedValidator,
)
from gcloud.core.apis.drf.resource_helpers import ViewSetResourceHelper
from gcloud.core.apis.drf.serilaziers.periodic_task import (
    CreatePeriodicTaskSerializer,
    PatchUpdatePeriodicTaskSerializer,
    PeriodicTaskListReadOnlySerializer,
    PeriodicTaskReadOnlySerializer,
)
from gcloud.core.apis.drf.viewsets.base import GcloudModelViewSet
from gcloud.core.models import Project
from gcloud.iam_auth import IAMMeta, res_factory
from gcloud.iam_auth.utils import get_common_flow_allowed_actions_for_user, get_flow_allowed_actions_for_user
from gcloud.periodictask.models import PeriodicTask
from gcloud.tasktmpl3.models import TaskTemplate
from gcloud.template_base.utils import replace_template_id
from gcloud.utils.strings import standardize_name
from pipeline_web.parser.validator import validate_web_pipeline_tree

logger = logging.getLogger("root")


class PeriodicTaskPermission(IamPermission):
    actions = {
        "update": IamPermissionInfo(
            IAMMeta.PERIODIC_TASK_EDIT_ACTION, res_factory.resources_for_periodic_task_obj, HAS_OBJECT_PERMISSION
        ),
        "partial_update": IamPermissionInfo(
            IAMMeta.PERIODIC_TASK_EDIT_ACTION, res_factory.resources_for_periodic_task_obj, HAS_OBJECT_PERMISSION
        ),
        "retrieve": IamPermissionInfo(
            IAMMeta.PERIODIC_TASK_VIEW_ACTION, res_factory.resources_for_periodic_task_obj, HAS_OBJECT_PERMISSION
        ),
        "destroy": IamPermissionInfo(
            IAMMeta.PERIODIC_TASK_DELETE_ACTION, res_factory.resources_for_periodic_task_obj, HAS_OBJECT_PERMISSION
        ),
    }

    def has_permission(self, request, view):
        if view.action == "list":
            user_type_validator = IamUserTypeBasedValidator()
            return user_type_validator.validate(request)
        elif view.action == "create":
            template_source = request.data.get("template_source", PROJECT)
            template_id = request.data.get("template_id")
            if template_source == PROJECT:
                iam_action = IAMMeta.FLOW_CREATE_PERIODIC_TASK_ACTION
                resources = res_factory.resources_for_flow(template_id)
            else:
                iam_action = IAMMeta.COMMON_FLOW_CREATE_PERIODIC_TASK_ACTION
                resources = res_factory.resources_for_common_flow(template_id)
                if request.data.get("project"):
                    resources.extend(res_factory.resources_for_project(request.data["project"]))
            self.iam_auth_check(request=request, action=iam_action, resources=resources)
            return True
        return super().has_permission(request, view)


class PeriodicTaskFilter(AllLookupSupportFilterSet):
    class Meta:
        model = PeriodicTask
        fields = {
            "id": ["exact"],
            "task__name": ["icontains"],
            "task__celery_task__enabled": ["exact"],
            "task__creator": ["exact"],
            "project__id": ["exact"],
            "editor": ["exact"],
            "task__last_run_at": ["gte", "lte"],
            "create_time": ["gte", "lte"],
            "edit_time": ["gte", "lte"],
        }


class PeriodicTaskViewSet(GcloudModelViewSet):
    queryset = PeriodicTask.objects.all()
    serializer_class = PeriodicTaskReadOnlySerializer
    filter_class = PeriodicTaskFilter
    pagination_class = LimitOffsetPagination
    iam_resource_helper = ViewSetResourceHelper(
        resource_func=res_factory.resources_for_periodic_task_obj,
        actions=[
            IAMMeta.PERIODIC_TASK_VIEW_ACTION,
            IAMMeta.PERIODIC_TASK_EDIT_ACTION,
            IAMMeta.PERIODIC_TASK_DELETE_ACTION,
        ],
    )
    permission_classes = [permissions.IsAuthenticated, PeriodicTaskPermission]
    project_multi_tenant_filter = True

    def get_serializer_class(self):
        if self.action == "list":
            return PeriodicTaskListReadOnlySerializer
        return PeriodicTaskReadOnlySerializer

    @staticmethod
    def _handle_serializer(request, serializer):
        template_source = serializer.validated_data["template_source"]
        template_id = serializer.validated_data["template_id"]
        project = serializer.validated_data["project"]
        pipeline_tree = serializer.validated_data["pipeline_tree"]
        name = serializer.validated_data["name"]
        if template_source == PROJECT:
            model_cls = TaskTemplate
            condition = {"id": template_id, "project": project, "is_deleted": False}
        elif template_source == COMMON:
            model_cls = CommonTemplate
            condition = {"id": template_id, "is_deleted": False}
        else:
            message = _(f"周期任务创建失败: 周期任务关联的流程[ID: {template_source}]不存在, 请检查配置 | _handle_serializer")
            logger.error(message)
            raise APIException(detail=message, code=err_code.REQUEST_PARAM_INVALID.code)

        try:
            template = model_cls.objects.filter(**condition).first()
        except model_cls.DoesNotExist:
            message = _(f"周期任务创建失败: 周期任务关联的公共流程[ID: {template_id}]不存在, 请检查配置 | _handle_serializer")
            logger.error(message)
            raise APIException(detail=message, code=err_code.REQUEST_PARAM_INVALID.code)
        try:
            replace_template_id(model_cls, pipeline_tree)
        except model_cls.DoesNotExist:
            message = _(f"周期任务创建失败: 周期任务关联的流程[ID: {template_id}]中, 子流程节点存在异常, 请检查配置 | _handle_serializer")
            logger.error(message)
            raise APIException(detail=message, code=err_code.REQUEST_PARAM_INVALID.code)

        # XSS handle
        name = standardize_name(name, PERIOD_TASK_NAME_MAX_LENGTH)
        username = request.user.username

        # validate pipeline tree
        try:
            validate_web_pipeline_tree(pipeline_tree)
        except PipelineException as e:
            message = str(e)
            raise APIException(detail=message, code=err_code.REQUEST_PARAM_INVALID.code)

        serializer.validated_data["template"] = template
        role = "editor" if serializer.instance else "creator"
        serializer.validated_data[role] = username
        serializer.validated_data["name"] = name
        serializer.validated_data["project"] = project
        serializer.validated_data["template_source"] = template_source
        serializer.validated_data["template_version"] = template.version
        return serializer

    def list(self, request, *args, **kwargs):
        project_id = int(request.query_params.get("project__id", 0)) or None

        if project_id:
            order_by = request.query_params.get("order_by") or "-id"
            orderings = ("-is_collected", "-task__celery_task__enabled", order_by)

            collection_task_ids, collection_task_map = Collection.objects.get_user_project_collection_instance_info(
                project_id=project_id, username=request.user.username, category="periodic_task"
            )

            queryset = (
                self.filter_queryset(self.get_queryset())
                .annotate(is_collected=ExpressionWrapper(Q(id__in=collection_task_ids), output_field=BooleanField()))
                .order_by(*orderings)
            )
        else:
            # 后台管理页面没有对应传参
            collection_task_ids, collection_task_map = [], {}
            queryset = self.filter_queryset(self.get_queryset())

        # 支持使用方配置不分页
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page if page else queryset, many=True)
        # 注入权限
        instances = self.injection_auth_actions(request, serializer.data, serializer.instance)
        # 获取并注入对应流程查看权限
        tmpl_data = {
            PROJECT: [inst["template_id"] for inst in instances if inst["template_source"] == PROJECT],
            COMMON: [inst["template_id"] for inst in instances if inst["template_source"] == COMMON],
        }
        template_view_actions = get_flow_allowed_actions_for_user(
            request.user.username, [IAMMeta.FLOW_VIEW_ACTION], tmpl_data[PROJECT]
        )
        common_template_view_actions = get_common_flow_allowed_actions_for_user(
            request.user.username, [IAMMeta.COMMON_FLOW_VIEW_ACTION], tmpl_data[COMMON]
        )
        view_actions = {
            PROJECT: template_view_actions,
            COMMON: common_template_view_actions,
        }
        for inst in instances:
            tmpl_id = str(inst["template_id"])
            tmpl_source = inst["template_source"]
            user_actions = view_actions.get(tmpl_source, {})
            view_action = IAMMeta.FLOW_VIEW_ACTION if tmpl_source == PROJECT else IAMMeta.COMMON_FLOW_VIEW_ACTION
            if tmpl_id in user_actions and user_actions[tmpl_id][view_action]:
                inst["auth_actions"].append(view_action)
            inst["is_collected"] = 1 if inst["id"] in collection_task_ids else 0
            inst["collection_id"] = collection_task_map.get(inst["id"], -1)
        return self.get_paginated_response(instances) if page is not None else Response(instances)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        bk_audit_add_event(
            username=request.user.username,
            action_id=IAMMeta.PERIODIC_TASK_VIEW_ACTION,
            resource_id=IAMMeta.PERIODIC_TASK_RESOURCE,
            instance=instance,
        )
        return super(PeriodicTaskViewSet, self).retrieve(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        bk_audit_add_event(
            username=request.user.username,
            action_id=IAMMeta.PERIODIC_TASK_DELETE_ACTION,
            resource_id=IAMMeta.PERIODIC_TASK_RESOURCE,
            instance=instance,
        )
        return super(PeriodicTaskViewSet, self).destroy(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = CreatePeriodicTaskSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        try:
            self._handle_serializer(request, serializer)
            instance = serializer.save()
        except PipelineException as e:
            raise ValidationException(e)
        instance.set_enabled(True)
        headers = self.get_success_headers(serializer.data)
        bk_audit_add_event(
            username=request.user.username,
            action_id=IAMMeta.FLOW_CREATE_PERIODIC_TASK_ACTION,
            resource_id=IAMMeta.PERIODIC_TASK_RESOURCE,
            instance=instance,
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = CreatePeriodicTaskSerializer(instance, data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        try:
            self._handle_serializer(request, serializer)
            instance = PeriodicTask.objects.update(instance, **serializer.validated_data)
        except PipelineException as e:
            raise ValidationException(e)
        bk_audit_add_event(
            username=request.user.username,
            action_id=IAMMeta.PERIODIC_TASK_EDIT_ACTION,
            resource_id=IAMMeta.PERIODIC_TASK_RESOURCE,
            instance=instance,
        )
        return Response(PeriodicTaskReadOnlySerializer(instance=instance).data)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = PatchUpdatePeriodicTaskSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            if "cron" in serializer.validated_data:
                project = Project.objects.filter(id=serializer.validated_data["project"]).first()
                instance.modify_cron(serializer.validated_data["cron"], project.time_zone)
            if "constants" in serializer.validated_data:
                instance.modify_constants(serializer.validated_data["constants"])
            if "name" in serializer.validated_data:
                instance.task.name = serializer.validated_data["name"]
                instance.task.save(update_fields=["name"])
            instance.editor = request.user.username
            instance.save(update_fields=["editor", "edit_time"])
            instance.task.creator = request.user.username
            instance.task.save()

        bk_audit_add_event(
            username=request.user.username,
            action_id=IAMMeta.PERIODIC_TASK_EDIT_ACTION,
            resource_id=IAMMeta.PERIODIC_TASK_RESOURCE,
            instance=instance,
        )

        return Response(PeriodicTaskReadOnlySerializer(instance=instance).data)
