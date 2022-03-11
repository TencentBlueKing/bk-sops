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

from rest_framework.response import Response
from rest_framework import serializers, generics, permissions
from django_filters import FilterSet

from iam.contrib.tastypie.shortcuts import allow_or_raise_immediate_response
from iam import Subject, Action

from gcloud.constants import TASK_NAME_MAX_LENGTH
from gcloud.utils.strings import standardize_name, standardize_pipeline_node_name
from gcloud.core.apis.drf.viewsets.base import GcloudReadOnlyViewSet
from gcloud.core.apis.drf.resource_helpers import ViewSetResourceHelper
from gcloud.core.apis.drf.serilaziers import (
    TaskFlowInstanceSerializer,
    CreateTaskFlowInstanceSerializer,
    RetrieveTaskFlowInstanceSerializer,
)
from gcloud.taskflow3.models import TaskFlowInstance, TimeoutNodeConfig
from gcloud.tasktmpl3.models import TaskTemplate
from gcloud.common_template.models import CommonTemplate
from gcloud.iam_auth.conf import TASK_ACTIONS
from pipeline.exceptions import PipelineException
from gcloud.core.models import EngineConfig
from gcloud.taskflow3.domains.auto_retry import AutoRetryNodeStrategyCreator
from gcloud.core.apis.drf.permission import IamPermission, IamPermissionInfo, HAS_OBJECT_PERMISSION, HAS_PERMISSION
from gcloud.iam_auth import IAMMeta, res_factory, get_iam_client
from gcloud.contrib.appmaker.models import AppMaker
from gcloud.contrib.operate_record.signal import operate_record_signal
from gcloud.contrib.operate_record.constants import OperateType, OperateSource, RecordType

iam = get_iam_client()


class TaskFlowFilterSet(FilterSet):
    class Meta:
        model = TaskFlowInstance
        fields = {
            "id": ["exact"],
            "category": ["exact"],
            "project__id": ["exact"],
            "pipeline_instance__creator": ["contains"],
            "pipeline_instance__executor": ["contains"],
            "pipeline_instance__name": ["icontains"],
            "pipeline_instance__is_started": ["exact"],
            "pipeline_instance__is_finished": ["exact"],
            "pipeline_instance__is_revoked": ["exact"],
            "create_method": ["exact"],
            "pipeline_instance__start_time": ["gte", "lte"],
        }


class TaskFlowInstancePermission(IamPermission):
    actions = {
        "list": IamPermissionInfo(IAMMeta.TASK_VIEW_ACTION),
        "retrieve": IamPermissionInfo(
            IAMMeta.TASK_VIEW_ACTION, res_factory.resources_for_task_obj, HAS_OBJECT_PERMISSION
        ),
        "destroy": IamPermissionInfo(
            IAMMeta.TASK_DELETE_ACTION, res_factory.resources_for_task_obj, HAS_OBJECT_PERMISSION
        ),
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
                allow_or_raise_immediate_response(
                    iam=iam,
                    system=IAMMeta.SYSTEM_ID,
                    subject=Subject("user", request.user.username),
                    action=Action(IAMMeta.MINI_APP_CREATE_TASK_ACTION),
                    resources=res_factory.resources_for_mini_app_obj(app_maker),
                )

            # flow create task perm
            else:
                template_source = request.data.get("template_source", "project")
                template_id = request.data.get("template", -1)
                model_cls = TaskTemplate if template_source == "project" else CommonTemplate
                try:
                    template = model_cls.objects.get(id=template_id)
                except model_cls.DoesNotExist:
                    return False
                allow_or_raise_immediate_response(
                    iam=iam,
                    system=IAMMeta.SYSTEM_ID,
                    subject=Subject("user", request.user.username),
                    action=Action(IAMMeta.FLOW_CREATE_TASK_ACTION),
                    resources=res_factory.resources_for_flow_obj(template),
                )
        return super().check_permission(request, view, check_hook=HAS_PERMISSION)


class TaskFlowInstanceViewSet(GcloudReadOnlyViewSet, generics.CreateAPIView, generics.DestroyAPIView):
    serializer_class = TaskFlowInstanceSerializer
    queryset = TaskFlowInstance.objects.filter(pipeline_instance__isnull=False, is_deleted=False).order_by(
        "pipeline_instance"
    )
    iam_resource_helper = ViewSetResourceHelper(
        resource_func=res_factory.resources_for_task_obj,
        actions=TASK_ACTIONS,
    )
    filter_class = TaskFlowFilterSet
    permission_classes = [permissions.IsAuthenticated, TaskFlowInstancePermission]
    ordering_fields = ["pipeline_instance"]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        # 支持使用方配置不分页
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page if page else queryset, many=True)
        # 注入权限
        data = self.injection_auth_actions(request, serializer.data, queryset)
        # 注入template_info（name、deleted
        # 项目流程
        template_ids = [
            int(instance["template_id"])
            for instance in data
            if instance["template_id"] and instance["template_source"] == "project"
        ]
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
            else:
                instance["template_name"] = common_template_info_map.get(instance["template_id"], {}).get("name")
                instance["template_deleted"] = common_template_info_map.get(instance["template_id"], {}).get(
                    "is_deleted", True
                )
        return self.get_paginated_response(data) if page is not None else Response(data)

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
            raise serializers.ValidationError(str(e))
        # set engine_ver
        serializer.validated_data["engine_ver"] = EngineConfig.objects.get_engine_ver(
            project_id=project.id, template_id=template.id, template_source=serializer.validated_data["template_source"]
        )
        # set extra_params
        serializer.validated_data["pipeline_instance"] = pipeline_instance
        serializer.validated_data["category"] = template.category
        serializer.validated_data["current_flow"] = (
            "func_clain" if serializer.validated_data["flow_type"] == "common_func" else "execute_task"
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
        # 记录操作流水
        operate_record_signal.send(
            sender=RecordType.task.name,
            operator=pipeline_instance_kwargs["creator"],
            operate_type=OperateType.create.name,
            operate_source=OperateSource.app.name,
            instance_id=serializer.instance.id,
            project_id=serializer.instance.project.id,
        )

    def perform_destroy(self, instance):
        if instance.is_started:
            if not (instance.is_finished or instance.is_revoked):
                raise serializers.ValidationError("无法删除未进入完成或撤销状态的流程")
        super().perform_destroy(instance)
        # 记录操作流水
        operate_record_signal.send(
            sender=RecordType.task.name,
            operator=self.request.user.username,
            operate_type=OperateType.delete.name,
            operate_source=OperateSource.app.name,
            instance_id=instance.id,
            project_id=instance.project.id,
        )

    def get_serializer_class(self, *args, **kwargs):
        if self.action == "create":
            return CreateTaskFlowInstanceSerializer
        elif self.action == "retrieve":
            return RetrieveTaskFlowInstanceSerializer
        return super().get_serializer_class(*args, **kwargs)
