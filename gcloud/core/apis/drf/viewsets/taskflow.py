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
import logging
import re
import typing
from datetime import datetime, timedelta

from bamboo_engine import states
from django.conf import settings
from django.db import transaction
from django.db.models import Q, QuerySet, Value
from django.utils.translation import gettext_lazy as _
from django_filters import FilterSet
from drf_yasg.utils import swagger_auto_schema
from pipeline.eri.models import State
from pipeline.exceptions import PipelineException
from pipeline.models import PipelineInstance, Snapshot
from rest_framework import generics, permissions, status
from rest_framework.decorators import action
from rest_framework.exceptions import ErrorDetail
from rest_framework.response import Response

from gcloud import err_code
from gcloud.analysis_statistics.models import TaskflowExecutedNodeStatistics
from gcloud.common_template.models import CommonTemplate
from gcloud.constants import COMMON, ONETIME, PROJECT, TASK_NAME_MAX_LENGTH, TaskCreateMethod, TaskExtraStatus
from gcloud.contrib.appmaker.models import AppMaker
from gcloud.contrib.audit.utils import bk_audit_add_event
from gcloud.contrib.function.models import FunctionTask
from gcloud.contrib.operate_record.constants import OperateSource, OperateType, RecordType
from gcloud.contrib.operate_record.signal import operate_record_signal
from gcloud.contrib.operate_record.utils import extract_extra_info
from gcloud.core.apis.drf.exceptions import ValidationException
from gcloud.core.apis.drf.permission import (
    HAS_OBJECT_PERMISSION,
    IamPermission,
    IamPermissionInfo,
    IamUserTypeBasedValidator,
)
from gcloud.core.apis.drf.resource_helpers import ViewSetResourceHelper
from gcloud.core.apis.drf.serilaziers import (
    CreateTaskFlowInstanceSerializer,
    ListChildrenTaskFlowQuerySerializer,
    ListChildrenTaskFlowResponseSerializer,
    NodeExecutionRecordQuerySerializer,
    NodeExecutionRecordResponseSerializer,
    NodeSnapshotQuerySerializer,
    NodeSnapshotResponseSerializer,
    RetrieveTaskFlowInstanceSerializer,
    RootTaskflowQuerySerializer,
    RootTaskflowResponseSerializer,
    TaskFlowInstanceListSerializer,
    TaskFlowInstanceSerializer,
)
from gcloud.core.apis.drf.viewsets import IAMMixin
from gcloud.core.apis.drf.viewsets.base import GcloudReadOnlyViewSet
from gcloud.core.models import EngineConfig
from gcloud.iam_auth import IAMMeta, get_iam_client, res_factory
from gcloud.iam_auth.conf import TASK_ACTIONS
from gcloud.iam_auth.utils import (
    get_common_flow_allowed_actions_for_user_and_project,
    get_flow_allowed_actions_for_user,
)
from gcloud.taskflow3.domains.auto_retry import AutoRetryNodeStrategyCreator
from gcloud.taskflow3.domains.dispatchers import TaskCommandDispatcher
from gcloud.taskflow3.models import TaskConfig, TaskFlowInstance, TaskFlowRelation, TimeoutNodeConfig
from gcloud.tasktmpl3.models import TaskTemplate
from gcloud.utils import concurrent
from gcloud.utils.strings import standardize_name, standardize_pipeline_node_name

logger = logging.getLogger("root")

iam = get_iam_client()


class TaskFLowStatusFilterHandler:
    FAILED = "failed"
    PAUSE = "pause"
    RUNNING = "running"
    PENDING_PROCESSING = "pending_processing"

    def __init__(self, status, queryset):
        """
        @param status: 状态
        @param queryset: task_instance queryset
        @param start_time: 查询开始时间
        """
        self.status = status
        # 只会查询v2的数据
        self.queryset = queryset

    def get_queryset(self):
        """
        当前支持失败和暂停状态，获取目标queryset
        @return:
        """
        if self.status == self.FAILED:
            return self._filter_failed()
        elif self.status == self.PAUSE:
            return self._filter_pipeline_pause()
        elif self.status == self.RUNNING:
            return self._filter_running()
        elif self.status == self.PENDING_PROCESSING:
            return self._filter_pending_process()
        else:
            return self.queryset

    def _get_pipeline_id_list(self):
        """
        获取当前符合条件的 pipeline_id 列表
        @return:
        """
        pipeline_instance_id_list = self.queryset.values_list("pipeline_instance_id", flat=True)

        pipeline_id_list = PipelineInstance.objects.filter(id__in=pipeline_instance_id_list).values_list(
            "instance_id", flat=True
        )

        return pipeline_id_list

    def _fetch_pipeline_instance_ids(self, statuses: typing.List[str], by_root: bool = True) -> QuerySet:
        pipeline_id_list = self._get_pipeline_id_list()
        # 暂停是针对于流程的暂停

        if len(statuses) == 1:
            query_kwargs: typing.Dict[str, typing.Any] = {"name": statuses[0]}
        else:
            query_kwargs: typing.Dict[str, typing.Any] = {"name__in": statuses}
        if by_root:
            query_kwargs["root_id__in"] = pipeline_id_list
        else:
            query_kwargs["node_id__in"] = pipeline_id_list
        pipeline_root_id_list = State.objects.filter(**query_kwargs).values("root_id").distinct()
        return PipelineInstance.objects.filter(instance_id__in=pipeline_root_id_list).values_list("id", flat=True)

    def _fetch_pause_pipeline_instance_ids(self):
        pipeline_id_list = self._get_pipeline_id_list()
        pipeline_pause_root_id_list = State.objects.filter(
            node_id__in=pipeline_id_list, name=states.SUSPENDED
        ).values_list("root_id", flat=True)

        pipeline_failed_root_id_list = State.objects.filter(
            root_id__in=pipeline_id_list, name=states.FAILED
        ).values_list("root_id", flat=True)

        pipeline_root_id_list = set(pipeline_pause_root_id_list) - set(pipeline_failed_root_id_list)
        return PipelineInstance.objects.filter(instance_id__in=pipeline_root_id_list).values_list("id", flat=True)

    def _fetch_pending_process_taskflow_ids(
        self, taskflow_instances: typing.List[TaskFlowInstance]
    ) -> typing.List[int]:
        def _get_task_status(taskflow_instance: TaskFlowInstance) -> typing.Dict[str, typing.Any]:
            dispatcher = TaskCommandDispatcher(
                engine_ver=taskflow_instance.engine_ver,
                taskflow_id=taskflow_instance.id,
                pipeline_instance=taskflow_instance.pipeline_instance,
                project_id=taskflow_instance.project_id,
            )
            get_task_status_result: typing.Dict[str, typing.Any] = dispatcher.get_task_status(
                with_ex_data=False, with_new_status=True
            )
            if get_task_status_result.get("result"):
                return {"id": taskflow_instance.id, "state": get_task_status_result["data"]["state"]}
            else:
                return {"id": taskflow_instance.id, "state": None}

        task_status_infos: typing.List[typing.Dict[str, typing.Any]] = concurrent.batch_call(
            _get_task_status,
            params_list=[{"taskflow_instance": taskflow_instance} for taskflow_instance in taskflow_instances],
        )

        pending_process_taskflow_ids: typing.List[int] = []
        for task_status_info in task_status_infos:
            if task_status_info["state"] == TaskExtraStatus.PENDING_PROCESSING.value:
                pending_process_taskflow_ids.append(task_status_info["id"])
        return pending_process_taskflow_ids

    def _filter_failed(self):
        """
        获取所有失败的任务，当任务失败时，任务的State的name会为Failed，去重可以获得当前存在失败节点的pipeline instance
        @return:
        """
        # root_id
        return self.queryset.filter(
            pipeline_instance_id__in=self._fetch_pipeline_instance_ids(statuses=[states.FAILED])
        )

    def _filter_pipeline_pause(self):
        """
        获取所有暂停的任务，当任务暂停时，pipeline 的状态会变成暂停，
        return:
        """
        pause_pipeline_instance_ids = self._fetch_pause_pipeline_instance_ids()
        return self.queryset.filter(pipeline_instance_id__in=pause_pipeline_instance_ids)

    def _filter_running(self):
        """
        正在运行的流程等于未完成的任务 -（暂停 + 失败的任务)

        @return:
        """

        running_task_queryset = self.queryset.exclude(
            pipeline_instance_id__in=self._fetch_pipeline_instance_ids(statuses=[states.FAILED, states.SUSPENDED])
        )
        pending_process_taskflow_ids: typing.List[int] = self._fetch_pending_process_taskflow_ids(running_task_queryset)
        return running_task_queryset.exclude(id__in=pending_process_taskflow_ids)

    def _filter_pending_process(self):
        """
        过滤出等待处理的流程
        :return:
        """
        # 找到所有正在执行中的流程
        # selected_related 只能在 objects 最前面加，此处先查处 ID 列表
        taskflow_instance_ids: typing.List[int] = list(
            self.queryset.exclude(
                pipeline_instance_id__in=self._fetch_pipeline_instance_ids(statuses=[states.FAILED])
            ).values_list("id", flat=True)
        )
        # selected_related 提前查取刚需的关联数据，避免 n+1 查询
        taskflow_instances: typing.List[TaskFlowInstance] = TaskFlowInstance.objects.select_related(
            "pipeline_instance"
        ).filter(id__in=taskflow_instance_ids)
        # 并行找到全部的等待执行任务
        pending_process_taskflow_ids: typing.List[int] = self._fetch_pending_process_taskflow_ids(taskflow_instances)
        return self.queryset.filter(id__in=pending_process_taskflow_ids)


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
        "node_snapshot_config": IamPermissionInfo(
            IAMMeta.TASK_VIEW_ACTION, res_factory.resources_for_task_obj, HAS_OBJECT_PERMISSION
        ),
        "node_execution_record": IamPermissionInfo(
            IAMMeta.TASK_VIEW_ACTION, res_factory.resources_for_task_obj, HAS_OBJECT_PERMISSION
        ),
        "convert_to_common_task": IamPermissionInfo(
            IAMMeta.TASK_OPERATE_ACTION, res_factory.resources_for_task_obj, HAS_OBJECT_PERMISSION
        ),
    }

    def has_permission(self, request, view):
        if view.action == "create":
            create_method = request.data.get("create_method")
            # mini app create task perm
            if create_method == TaskCreateMethod.APP_MAKER.value:
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
        elif view.action in ["list", "list_children_taskflow", "root_task_info", "task_count"]:
            user_type_validator = IamUserTypeBasedValidator()
            return user_type_validator.validate(request)
        return super().has_permission(request, view)


class TaskFlowInstanceViewSet(GcloudReadOnlyViewSet, generics.CreateAPIView, generics.DestroyAPIView):
    serializer_class = TaskFlowInstanceSerializer
    queryset = TaskFlowInstance.objects.filter(
        pipeline_instance__isnull=False, is_deleted=Value(0), pipeline_instance__is_expired=False
    ).order_by("-id")
    iam_resource_helper = ViewSetResourceHelper(resource_func=res_factory.resources_for_task_obj, actions=TASK_ACTIONS)
    filter_class = TaskFlowFilterSet
    permission_classes = [permissions.IsAuthenticated, TaskFlowInstancePermission]

    def _get_queryset(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        delta_time = (
            settings.MY_DYNAMIC_LIST_FILTER_DAYS
            if "creator_or_executor" in request.query_params
            else settings.TASK_LIST_STATUS_FILTER_DAYS
        )
        start_time = datetime.now() - timedelta(days=delta_time)
        queryset = queryset.filter(
            pipeline_instance__create_time__gte=start_time,
            project__tenant_id=request.user.tenant_id,
        )
        # 该实现存在性能问题，需要优化
        # task_instance_status = request.query_params.get("task_instance_status")
        # if task_instance_status:
        #     # 状态查询的范围为最近TASK_LIST_STATUS_FILTER_DAYS天内，已经开始的v2引擎的任务
        #     queryset = queryset.filter(
        #         pipeline_instance__start_time__gte=start_time, engine_ver=EngineConfig.ENGINE_VER_V2
        #     )
        #     queryset = TaskFLowStatusFilterHandler(status=task_instance_status, queryset=queryset).get_queryset()
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self._get_queryset(request)

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
        elif "without_count" in request.query_params:
            # 该场景不需要翻页，不调用qs.count()优化查询效率
            self.paginator.limit = self.paginator.get_limit(request)
            self.paginator.offset = self.paginator.get_offset(request)
            self.paginator.count = -1
            self.paginator.request = request
            page = list(queryset[self.paginator.offset : self.paginator.offset + self.paginator.limit])
        else:
            page = self.paginate_queryset(queryset)

        serializer = self.get_serializer(page, many=True)
        # 注入权限
        data = self.injection_auth_actions(request, serializer.data, page)
        self._inject_template_related_info(request, data)
        return self.get_paginated_response(data) if page is not None else Response(data)

    @swagger_auto_schema(
        method="GET",
        operation_summary="获取任务总数",
    )
    @action(methods=["GET"], detail=False)
    def task_count(self, request, *args, **kwargs):
        queryset = self._get_queryset(request)
        return Response({"count": queryset.count()})

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
        common_templates_allowed_actions = get_common_flow_allowed_actions_for_user_and_project(
            request.user.username,
            [IAMMeta.COMMON_FLOW_VIEW_ACTION, IAMMeta.COMMON_FLOW_CREATE_TASK_ACTION],
            common_template_ids,
            request.query_params.get("project_id"),
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

        template_id__allowed_actions_map = {}

        if data["template_source"] == COMMON:
            template_id__allowed_actions_map = get_common_flow_allowed_actions_for_user_and_project(
                request.user.username,
                [IAMMeta.COMMON_FLOW_VIEW_ACTION, IAMMeta.COMMON_FLOW_CREATE_ACTION],
                [data["template_id"]],
                str(instance.project_id),
            )
        elif data["template_source"] == PROJECT:
            template_id__allowed_actions_map = get_flow_allowed_actions_for_user(
                request.user.username,
                [IAMMeta.FLOW_VIEW_ACTION, IAMMeta.FLOW_CREATE_TASK_ACTION],
                [data["template_id"]],
            )

        for act, allowed in (template_id__allowed_actions_map.get(str(data["template_id"])) or {}).items():
            if allowed:
                data["auth_actions"].append(act)

        bk_audit_add_event(
            username=request.user.username,
            action_id=IAMMeta.TASK_VIEW_ACTION,
            resource_id=IAMMeta.TASK_RESOURCE,
            instance=instance,
        )
        return Response(data)

    @staticmethod
    def handle_task_name_attr(data):
        data["name"] = standardize_name(data["name"], TASK_NAME_MAX_LENGTH)
        standardize_pipeline_node_name(data["pipeline_tree"])

    def perform_create(self, serializer):
        template = serializer.validated_data.pop("template")
        project = serializer.validated_data["project"]
        # create pipeline_instance
        creator = serializer.validated_data.pop("creator")
        pipeline_instance_kwargs = {
            "name": serializer.validated_data.pop("name"),
            "creator": creator,
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
            sender=RecordType.task,
            operator=pipeline_instance_kwargs["creator"],
            operate_type=OperateType.create.name,
            operate_source=OperateSource.app.name,
            instance_id=serializer.instance.id,
            project_id=serializer.instance.project.id,
            extra_info=extra_info,
        )
        action_id_mappings = {
            PROJECT: IAMMeta.FLOW_CREATE_TASK_ACTION,
            COMMON: IAMMeta.COMMON_FLOW_CREATE_TASK_ACTION,
            ONETIME: IAMMeta.PROJECT_FAST_CREATE_TASK_ACTION,
        }
        if serializer.validated_data.get("create_method") == "app_maker":
            bk_audit_add_event(
                username=creator,
                action_id=IAMMeta.MINI_APP_CREATE_TASK_ACTION,
                resource_id=IAMMeta.TASK_RESOURCE,
                instance=serializer.instance,
            )
        elif serializer.validated_data.get("template_source") in action_id_mappings:
            bk_audit_add_event(
                username=creator,
                action_id=action_id_mappings[serializer.validated_data["template_source"]],
                resource_id=IAMMeta.TASK_RESOURCE,
                instance=serializer.instance,
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
            sender=RecordType.task,
            operator=self.request.user.username,
            operate_type=OperateType.delete.name,
            operate_source=OperateSource.app.name,
            instance_id=instance.id,
            project_id=instance.project.id,
        )
        bk_audit_add_event(
            username=request.user.username,
            action_id=IAMMeta.TASK_DELETE_ACTION,
            resource_id=IAMMeta.TASK_RESOURCE,
            instance=instance,
        )
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_serializer_class(self, *args, **kwargs):
        if self.action == "create":
            return CreateTaskFlowInstanceSerializer
        elif self.action == "list":
            return TaskFlowInstanceListSerializer
        elif self.action == "retrieve":
            return RetrieveTaskFlowInstanceSerializer
        return super().get_serializer_class(*args, **kwargs)

    @staticmethod
    def _optimized_my_dynamic_query(queryset, username, limit, offset, create_method=None):
        """
        优化我的动态接口查询速度
        """
        original_query, params = queryset.query.sql_with_params()
        new_query = re.sub(
            "FROM (.*?) ON",
            "FROM `pipeline_pipelineinstance` STRAIGHT_JOIN `taskflow3_taskflowinstance` ON",
            original_query,
        )
        new_query = re.sub("ORDER BY (.*?) DESC", "ORDER BY `pipeline_pipelineinstance`.`create_time` DESC", new_query)
        new_query += f" LIMIT {limit} OFFSET {offset}"
        return TaskFlowInstance.objects.raw(new_query, params)

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
            id__in=children_task_ids, pipeline_instance__isnull=False, is_deleted=Value(0)
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
    @action(methods=["GET"], detail=True)
    def node_execution_record(self, request, *args, **kwargs):
        params = NodeExecutionRecordQuerySerializer(data=request.query_params)
        params.is_valid(raise_exception=True)
        template_node_id = params.data["template_node_id"]
        task = self.get_object()
        execution_data = (
            TaskflowExecutedNodeStatistics.objects.filter(
                template_node_id=template_node_id, status=True, is_skip=False, trigger_template_id=task.template_id
            )
            .order_by("-archived_time")
            .values("archived_time", "elapsed_time")
        )
        execution_total_time = len(execution_data)
        execution_time_data = execution_data[: settings.MAX_RECORDED_NODE_EXECUTION_TIMES]
        node_execution_record_serializer = NodeExecutionRecordResponseSerializer(
            data={"execution_time": execution_time_data, "total": execution_total_time}
        )
        node_execution_record_serializer.is_valid(raise_exception=True)
        return Response(node_execution_record_serializer.validated_data)

    @swagger_auto_schema(method="GET", operation_summary="查询任务是否支持重试填参")
    @action(methods=["GET"], detail=True)
    def enable_fill_retry_params(self, request, *args, **kwargs):
        task_id = kwargs["pk"]
        return Response({"enable": TaskConfig.objects.enable_fill_retry_params(task_id)})

    @swagger_auto_schema(
        method="GET",
        operation_summary="获取某个节点的节点配置快照",
        query_serializer=NodeSnapshotQuerySerializer,
        responses={200: NodeSnapshotResponseSerializer},
    )
    @action(methods=["GET"], detail=True)
    def node_snapshot_config(self, request, *args, **kwargs):
        """
        获取某个节点的快照配置
        params: subprocess_stack 堆栈信息
        param: node_id: 节点 ID, string, query, required
        return: dict 根据 result 字段判断是否请求成功
        {
            "result": true, 根据result 判断是否正常
            "data": {
                "component": {
                    "code": "sleep_timer",
                    "data": {
                        "bk_timing": {
                            "hook": false,
                            "need_render": true,
                            "value": "10"
                        },
                        "force_check": {
                            "hook": false,
                            "need_render": true,
                            "value": true
                        }
                    },
                    "version": "legacy"
                },
                "error_ignorable": false,
                "id": "node7a63244b7837ef15ef3b474b47bd",
                "incoming": [
                    "line02c5d5f7d1b996bb050f153e077b"
                ],
                "loop": null,
                "name": "定时",
                "optional": true,
                "outgoing": "linee702fc4ff57920950c78e987ea96",
                "stage_name": "",
                "type": "ServiceActivity",
                "retryable": true,
                "skippable": true,
                "auto_retry": {
                    "enable": false,
                    "interval": 0,
                    "times": 1
                },
                "timeout_config": {
                    "enable": false,
                    "seconds": 10,
                    "action": "forced_fail"
                }
            }
        }

        """
        ser = NodeSnapshotQuerySerializer(data=request.GET)
        ser.is_valid(raise_exception=True)

        node_id = ser.data["node_id"]
        subprocess_stack = ser.data["subprocess_stack"]
        task = self.get_object()

        execution_data = task.pipeline_instance.execution_data

        # 如果存在子流程
        if subprocess_stack:

            version = {}

            def _get_node_info(pipeline: dict, subprocess_stack: list):
                # go deeper
                if subprocess_stack:
                    component_act = pipeline["activities"][subprocess_stack[0]]
                    version["version_id"] = component_act.get("version")
                    return _get_node_info(component_act["pipeline"], subprocess_stack[1:])

                return pipeline["activities"][node_id]

            node_info = _get_node_info(execution_data, subprocess_stack)
            version_id = version.get("version_id")
            template_node_id = node_info.get("template_node_id")
            # 如果没有拿到对应的template_node_id，直接返回
            if version_id is None or template_node_id is None:
                return Response()

            snapshot_data = Snapshot.objects.filter(md5sum=version_id).order_by("-id").first().data
            snapshot_node_info = snapshot_data["activities"].get(template_node_id)
            return Response(snapshot_node_info)

        # 不存在子流程，则直接查找
        template_node_id = execution_data["activities"].get(node_id, {}).get("template_node_id")

        # 旧的流程拿不到模板node_id, 直接返回空即可
        if template_node_id is None:
            return Response()

        node_snapshot_config = task.pipeline_instance.snapshot.data["activities"].get(template_node_id)
        return Response(node_snapshot_config)

    @swagger_auto_schema(method="POST", operation_summary="职能化任务转化为普通任务，并删除关联的职能化任务")
    @action(methods=["POST"], detail=True)
    def convert_to_common_task(self, request, *args, **kwargs):
        task = self.get_object()
        if task.creator != request.user.username:
            return Response({"result": False, "message": "Only task creator can do this action.", "data": None})
        if task.current_flow != "func_claim":
            return Response(
                {
                    "result": False,
                    "message": "Only task with current_flow of func_claim can be converted.",
                    "data": None,
                }
            )
        func_task_qs = FunctionTask.objects.filter(task_id=task.id)
        if task.flow_type != "common_func" or len(func_task_qs) != 1:
            return Response(
                {
                    "result": False,
                    "message": "the flow_type of task should be common_func and "
                    "the number of corresponding function task should be 1. ",
                }
            )
        with transaction.atomic():
            task.flow_type = "common"
            task.current_flow = "execute_task"
            task.save(update_fields=["flow_type", "current_flow"])
            FunctionTask.objects.filter(task_id=task.id).delete()
        return Response({"result": True, "message": "convert to common task success", "data": None})
