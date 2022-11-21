# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2022 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
import re

from django.conf import settings
from django.db.models import Q
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ErrorDetail
from rest_framework import generics, permissions, status
from django_filters import FilterSet

from gcloud.analysis_statistics.models import TaskflowExecutedNodeStatistics
from gcloud.constants import TASK_NAME_MAX_LENGTH
from gcloud import err_code
from gcloud.core.apis.drf.exceptions import ValidationException
from gcloud.core.apis.drf.viewsets import IAMMixin
from gcloud.utils.strings import standardize_name, standardize_pipeline_node_name
from gcloud.core.apis.drf.viewsets.base import GcloudReadOnlyViewSet
from gcloud.core.apis.drf.resource_helpers import ViewSetResourceHelper
from gcloud.core.apis.drf.serilaziers import (
    TaskFlowInstanceSerializer,
    CreateTaskFlowInstanceSerializer,
    RetrieveTaskFlowInstanceSerializer,
    ListChildrenTaskFlowQuerySerializer,
    ListChildrenTaskFlowResponseSerializer,
    RootTaskflowQuerySerializer,
    RootTaskflowResponseSerializer,
    NodeExecutionRecordQuerySerializer,
    NodeExecutionRecordResponseSerializer,
)
from gcloud.taskflow3.models import TaskFlowInstance, TimeoutNodeConfig, TaskFlowRelation, TaskConfig
from gcloud.tasktmpl3.models import TaskTemplate
from gcloud.common_template.models import CommonTemplate
from gcloud.iam_auth.conf import TASK_ACTIONS
from pipeline.exceptions import PipelineException
from gcloud.core.models import EngineConfig
from gcloud.taskflow3.domains.auto_retry import AutoRetryNodeStrategyCreator
from gcloud.core.apis.drf.permission import (
    IamPermission,
    IamPermissionInfo,
    HAS_OBJECT_PERMISSION,
    IamUserTypeBasedValidator,
)
from gcloud.iam_auth import IAMMeta, res_factory, get_iam_client
from gcloud.contrib.appmaker.models import AppMaker
from gcloud.contrib.operate_record.signal import operate_record_signal
from gcloud.contrib.operate_record.constants import OperateType, OperateSource, RecordType
from gcloud.iam_auth.utils import get_flow_allowed_actions_for_user, get_common_flow_allowed_actions_for_user
from gcloud.contrib.operate_record.utils import extract_extra_info
from django.utils.translation import ugettext_lazy as _
import logging

logger = logging.getLogger("root")

iam = get_iam_client()


class TaskFlowFilterSet(FilterSet):
    class Meta:
        model = TaskFlowInstance
        fields = {
            "id": ["exact"],
            "template_id": ["exact"],
            "template_source": ["exact"],
            "category": ["exact"],
            "project__id": ["exact"],
            "pipeline_instance__creator": ["contains"],
            "pipeline_instance__executor": ["contains"],
            "pipeline_instance__name": ["icontains"],
            "pipeline_instance__is_started": ["exact"],
            "pipeline_instance__is_finished": ["exact"],
            "pipeline_instance__is_revoked": ["exact"],
            "create_method": ["exact"],
            "create_info": ["exact"],
            "recorded_executor_proxy": ["exact"],
            "pipeline_instance__start_time": ["gte", "lte"],
            "pipeline_instance__finish_time": ["gte", "lte"],
            "pipeline_instance__create_time": ["gte", "lte"],
            "is_child_taskflow": ["exact"],
        }


class TaskFlowInstancePermission(IamPermission, IAMMixin):
    actions = {
        "retrieve": IamPermissionInfo(
            IAMMeta.TASK_VIEW_ACTION, res_factory.resources_for_task_obj, HAS_OBJECT_PERMISSION
        ),
        "destroy": IamPermissionInfo(
            IAMMeta.TASK_DELETE_ACTION, res_factory.resources_for_task_obj, HAS_OBJECT_PERMISSION
        ),
        "enable_fill_retry_params": IamPermissionInfo(pass_all=True),
    }

    def has_permission(self, request, view):
        if view.action == "create":
            create_method = request.data.get("create_method")
            # mini app create task perm
            if create_method == "app_maker":
                app_maker_id = request.data["create_info"]
                try:
                    app_maker = AppMaker.objects.get(id=app_maker_id)
                except AppMaker.DoesNotExist:
                    return False
                self.iam_auth_check(
                    request=request,
                    action=IAMMeta.MINI_APP_CREATE_TASK_ACTION,
                    resources=res_factory.resources_for_mini_app_obj(app_maker),
                )
                return True
            # flow create task perm
            else:
                template_source = request.data.get("template_source", "project")
                template_id = int(request.data.get("template", -1))
                model_cls = TaskTemplate if template_source == "project" else CommonTemplate
                try:
                    template = model_cls.objects.get(id=template_id)
                except model_cls.DoesNotExist:
                    return False
                if template_source == "project":
                    iam_action = IAMMeta.FLOW_CREATE_TASK_ACTION
                    resources = res_factory.resources_for_flow_obj(template)
                else:
                    iam_action = IAMMeta.COMMON_FLOW_CREATE_TASK_ACTION
                    resources = res_factory.resources_for_common_flow_obj(template)
                    if request.data.get("project"):
                        resources.extend(res_factory.resources_for_project(request.data["project"]))
                self.iam_auth_check(request=request, action=iam_action, resources=resources)
                return True
        elif view.action in ["list", "list_children_taskflow", "root_task_info", "node_execution_record"]:
            user_type_validator = IamUserTypeBasedValidator()
            return user_type_validator.validate(request)
        return super().has_permission(request, view)


class TaskFlowInstanceViewSet(GcloudReadOnlyViewSet, generics.CreateAPIView, generics.DestroyAPIView):
    serializer_class = TaskFlowInstanceSerializer
    queryset = TaskFlowInstance.objects.filter(
        pipeline_instance__isnull=False, is_deleted=False, pipeline_instance__is_expired=False
    ).order_by("-id")
    iam_resource_helper = ViewSetResourceHelper(resource_func=res_factory.resources_for_task_obj, actions=TASK_ACTIONS)
    filter_class = TaskFlowFilterSet
    permission_classes = [permissions.IsAuthenticated, TaskFlowInstancePermission]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        # [我的动态] 接口过滤
        if "creator_or_executor" in request.query_params:
            queryset = queryset.filter(
                Q(pipeline_instance__executor=request.user.username)
                | Q(pipeline_instance__creator=request.user.username)
            )
            # 该场景不需要翻页，不调用qs.count()优化查询效率
            self.paginator.limit = self.paginator.get_limit(request)
            self.paginator.offset = self.paginator.get_offset(request)
            self.paginator.count = -1
            create_method = request.query_params.get("create_method")
            queryset = self._optimized_my_dynamic_query(
                queryset, request.user.username, self.paginator.limit, self.paginator.offset, create_method
            )
            page = list(queryset)
        else:
            page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        # 注入权限
        data = self.injection_auth_actions(request, serializer.data, page)
        self._inject_template_related_info(request, data)
        return self.get_paginated_response(data) if page is not None else Response(data)

    @staticmethod
    def _inject_template_related_info(request, data):
        # 注入template_info（name、deleted
        # 项目流程
        template_ids = [
            int(instance["template_id"])
            for instance in data
            if instance["template_id"] and instance["template_source"] == "project"
        ]
        # 注入流程相关权限
        templates_allowed_actions = get_flow_allowed_actions_for_user(
            request.user.username, [IAMMeta.FLOW_VIEW_ACTION, IAMMeta.FLOW_CREATE_TASK_ACTION], template_ids
        )
        template_info = TaskTemplate.objects.filter(id__in=template_ids).values(
            "id", "pipeline_template__name", "is_deleted"
        )
        template_info_map = {
            str(t["id"]): {"name": t["pipeline_template__name"], "is_deleted": t["is_deleted"]} for t in template_info
        }
        # 公共流程
        common_template_ids = [
            int(instance["template_id"])
            for instance in data
            if instance["template_id"] and instance["template_source"] == "common"
        ]
        common_templates_allowed_actions = get_common_flow_allowed_actions_for_user(
            request.user.username,
            [IAMMeta.COMMON_FLOW_VIEW_ACTION, IAMMeta.COMMON_FLOW_CREATE_TASK_ACTION],
            common_template_ids,
        )
        common_template_info = CommonTemplate.objects.filter(id__in=common_template_ids).values(
            "id", "pipeline_template__name", "is_deleted"
        )
        common_template_info_map = {
            str(t["id"]): {"name": t["pipeline_template__name"], "is_deleted": t["is_deleted"]}
            for t in common_template_info
        }
        for instance in data:
            if instance["template_source"] == "project":
                instance["template_name"] = template_info_map.get(instance["template_id"], {}).get("name")
                instance["template_deleted"] = template_info_map.get(instance["template_id"], {}).get(
                    "is_deleted", True
                )
                for act, allowed in templates_allowed_actions.get(str(instance["template_id"]), {}).items():
                    if allowed:
                        instance["auth_actions"].append(act)
            else:
                instance["template_name"] = common_template_info_map.get(instance["template_id"], {}).get("name")
                instance["template_deleted"] = common_template_info_map.get(instance["template_id"], {}).get(
                    "is_deleted", True
                )
                for act, allowed in common_templates_allowed_actions.get(str(instance["template_id"]), {}).items():
                    if allowed:
                        instance["auth_actions"].append(act)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.pipeline_instance.is_expired:
            return Response({"detail": ErrorDetail("任务已过期", err_code.REQUEST_PARAM_INVALID.code)}, exception=True)
        serializer = self.get_serializer(instance)
        # 注入权限
        data = self.injection_auth_actions(request, serializer.data, instance)
        return Response(data)

    @staticmethod
    def handle_task_name_attr(data):
        data["name"] = standardize_name(data["name"], TASK_NAME_MAX_LENGTH)
        standardize_pipeline_node_name(data["pipeline_tree"])

    def perform_create(self, serializer):
        template = serializer.validated_data.pop("template")
        project = serializer.validated_data["project"]
        # create pipeline_instance
        pipeline_instance_kwargs = {
            "name": serializer.validated_data.pop("name"),
            "creator": serializer.validated_data.pop("creator"),
            "pipeline_tree": serializer.validated_data.pop("pipeline_tree"),
            "description": serializer.validated_data.pop("description"),
        }
        # XSS handle
        self.handle_task_name_attr(pipeline_instance_kwargs)
        try:
            pipeline_instance = TaskFlowInstance.objects.create_pipeline_instance(template, **pipeline_instance_kwargs)
        except PipelineException as e:
            raise ValidationException(e)
        # set engine_ver
        serializer.validated_data["engine_ver"] = EngineConfig.objects.get_engine_ver(
            project_id=project.id, template_id=template.id, template_source=serializer.validated_data["template_source"]
        )
        # set extra_params
        serializer.validated_data["pipeline_instance"] = pipeline_instance
        serializer.validated_data["category"] = template.category
        serializer.validated_data["current_flow"] = (
            "func_claim" if serializer.validated_data["flow_type"] == "common_func" else "execute_task"
        )
        serializer.validated_data["template_id"] = template.id
        # create taskflow
        serializer.save()
        # crete auto retry strategy
        arn_creator = AutoRetryNodeStrategyCreator(
            taskflow_id=serializer.instance.id, root_pipeline_id=pipeline_instance.instance_id
        )
        arn_creator.batch_create_strategy(pipeline_instance.execution_data)

        # create timeout config
        TimeoutNodeConfig.objects.batch_create_node_timeout_config(
            taskflow_id=serializer.instance.id,
            root_pipeline_id=pipeline_instance.instance_id,
            pipeline_tree=pipeline_instance.execution_data,
        )
        constants = pipeline_instance.execution_data.get("constants")
        extra_info = extract_extra_info(constants)
        # 记录操作流水
        operate_record_signal.send(
            sender=RecordType.task.name,
            operator=pipeline_instance_kwargs["creator"],
            operate_type=OperateType.create.name,
            operate_source=OperateSource.app.name,
            instance_id=serializer.instance.id,
            project_id=serializer.instance.project.id,
            extra_info=extra_info,
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.is_started:
            if not (instance.is_finished or instance.is_revoked):
                message = _("任务删除失败: 仅允许删除[未执行]任务, 请检查任务状态")
                logger.error(message)
                return Response({"detail": ErrorDetail(message, err_code.REQUEST_PARAM_INVALID.code)}, exception=True)
        self.perform_destroy(instance)
        # 记录操作流水
        operate_record_signal.send(
            sender=RecordType.task.name,
            operator=self.request.user.username,
            operate_type=OperateType.delete.name,
            operate_source=OperateSource.app.name,
            instance_id=instance.id,
            project_id=instance.project.id,
        )
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_serializer_class(self, *args, **kwargs):
        if self.action == "create":
            return CreateTaskFlowInstanceSerializer
        elif self.action == "retrieve":
            return RetrieveTaskFlowInstanceSerializer
        return super().get_serializer_class(*args, **kwargs)

    @staticmethod
    def _optimized_my_dynamic_query(queryset, username, limit, offset, create_method=None):
        """
        优化我的动态接口查询速度
        """
        original_query = str(queryset.query)
        new_query = re.sub(
            "FROM (.*?) ON",
            "FROM `pipeline_pipelineinstance` STRAIGHT_JOIN `taskflow3_taskflowinstance` ON",
            original_query,
        )
        new_query = re.sub("ORDER BY (.*?) DESC", "ORDER BY `pipeline_pipelineinstance`.`id` DESC", new_query)
        new_query = new_query.replace(username, f"'{username}'")
        if create_method:
            new_query = new_query.replace(create_method, f"'{create_method}'")
        new_query += f" LIMIT {limit} OFFSET {offset}"
        return TaskFlowInstance.objects.raw(new_query)

    @swagger_auto_schema(
        method="GET",
        operation_summary="获取某个任务的子任务列表",
        query_serializer=ListChildrenTaskFlowQuerySerializer,
        responses={200: ListChildrenTaskFlowResponseSerializer},
    )
    @action(methods=["GET"], detail=False)
    def list_children_taskflow(self, request, *args, **kwargs):
        root_task_id = request.query_params.get("root_task_id")
        children_task_info = TaskFlowRelation.objects.filter(root_task_id=root_task_id).values(
            "task_id", "parent_task_id"
        )
        children_task_ids = [info["task_id"] for info in children_task_info]
        queryset = TaskFlowInstance.objects.filter(
            id__in=children_task_ids, pipeline_instance__isnull=False, is_deleted=False
        )
        queryset = self.filter_queryset(queryset)
        serializer = self.get_serializer(queryset, many=True)
        data = self.injection_auth_actions(request, serializer.data, queryset)
        self._inject_template_related_info(request, data)

        relations = {}
        for info in children_task_info:
            relations.setdefault(info["parent_task_id"], []).append(info["task_id"])
        return Response({"tasks": data, "relations": relations})

    @swagger_auto_schema(
        method="GET",
        operation_summary="批量获取任务是否有独立子任务",
        query_serializer=RootTaskflowQuerySerializer,
        responses={200: RootTaskflowResponseSerializer},
    )
    @action(methods=["GET"], detail=False)
    def root_task_info(self, request, *args, **kwargs):
        task_ids = request.query_params.get("task_ids") or []
        if task_ids:
            task_ids = [int(task_id) for task_id in task_ids.split(",")]
        root_task_ids = TaskFlowRelation.objects.filter(root_task_id__in=task_ids).values_list(
            "root_task_id", flat=True
        )
        root_task_info = {task_id: True if task_id in root_task_ids else False for task_id in task_ids}
        return Response({"has_children_taskflow": root_task_info})

    @swagger_auto_schema(
        methods=["GET"],
        operation_summary="获取节点历史执行记录数据",
        query_serializer=NodeExecutionRecordQuerySerializer,
        responses={200: NodeExecutionRecordResponseSerializer},
    )
    @action(methods=["GET"], detail=False)
    def node_execution_record(self, request, *args, **kwargs):
        template_node_id = request.query_params.get("template_node_id")
        execution_time_data = (
            TaskflowExecutedNodeStatistics.objects.filter(template_node_id=template_node_id, status=True, is_skip=False)
            .order_by("-archived_time")
            .values("archived_time", "elapsed_time")
        )[: settings.MAX_RECORDED_NODE_EXECUTION_TIMES]
        node_execution_record_serializer = NodeExecutionRecordResponseSerializer(
            data={"execution_time": execution_time_data}
        )
        node_execution_record_serializer.is_valid(raise_exception=True)
        return Response(node_execution_record_serializer.validated_data)

    @swagger_auto_schema(method="GET", operation_summary="查询任务是否支持重试填参")
    @action(methods=["GET"], detail=True)
    def enable_fill_retry_params(self, request, *args, **kwargs):
        task_id = kwargs["pk"]
        return Response({"enable": TaskConfig.objects.enable_fill_retry_params(task_id)})
