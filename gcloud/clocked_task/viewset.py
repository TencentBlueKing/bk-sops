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

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status, viewsets
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response

from gcloud.clocked_task.models import ClockedTask
from gcloud.clocked_task.permissions import ClockedTaskPermissions
from gcloud.clocked_task.serializer import ClockedTaskPatchSerializer, ClockedTaskSerializer
from gcloud.core.apis.drf.viewsets import ApiMixin, IAMMixin, MultiTenantMixin
from gcloud.iam_auth import IAMMeta, get_iam_client
from gcloud.iam_auth.resource_helpers.clocked_task import ClockedTaskResourceHelper
from gcloud.iam_auth.utils import get_flow_allowed_actions_for_user

iam = get_iam_client()


class ClockedTaskViewSet(ApiMixin, IAMMixin, MultiTenantMixin, viewsets.ModelViewSet):
    queryset = ClockedTask.objects.all()
    permission_classes = [permissions.IsAuthenticated, ClockedTaskPermissions]
    serializer_class = ClockedTaskSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        "id": ["exact"],
        "creator": ["exact"],
        "editor": ["exact"],
        "plan_start_time": ["gte", "lte"],
        "edit_time": ["gte", "lte"],
        "create_time": ["gte", "lte"],
        "task_name": ["exact", "icontains", "contains"],
        "project_id": ["exact"],
        "state": ["exact"],
    }
    pagination_class = LimitOffsetPagination
    iam_resource_helper = ClockedTaskResourceHelper(
        iam=iam,
        system=IAMMeta.SYSTEM_ID,
        actions=[
            IAMMeta.CLOCKED_TASK_VIEW_ACTION,
            IAMMeta.CLOCKED_TASK_EDIT_ACTION,
            IAMMeta.CLOCKED_TASK_DELETE_ACTION,
        ],
    )
    project_id_multi_tenant_filter = True

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        instances = page if page is not None else list(queryset)
        serializer = self.get_serializer(instances, many=True)
        deserialized_instances = serializer.data
        auth_actions = self.iam_get_instances_auth_actions(request, instances) or {}
        template_view_actions = get_flow_allowed_actions_for_user(
            request.user.username, [IAMMeta.FLOW_VIEW_ACTION], [inst.template_id for inst in instances]
        )
        for deserialized_instance in deserialized_instances:
            deserialized_instance["auth_actions"] = auth_actions.get(deserialized_instance["id"], [])
            tmpl_id = str(deserialized_instance["template_id"])
            if tmpl_id in template_view_actions and template_view_actions[tmpl_id][IAMMeta.FLOW_VIEW_ACTION]:
                deserialized_instance["auth_actions"].append(IAMMeta.FLOW_VIEW_ACTION)
        return (
            self.get_paginated_response(deserialized_instances)
            if page is not None
            else Response(deserialized_instances)
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        deserialized_instance = serializer.data
        auth_actions = self.iam_get_instance_auth_actions(request, instance)
        if auth_actions:
            deserialized_instance["auth_actions"] = auth_actions
        return Response(deserialized_instance)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        validated_data["creator"] = request.user.username
        task = ClockedTask.objects.create_task(**validated_data)
        response_serializer = self.serializer_class(instance=task)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if "plan_start_time" in request.data:
            serializer = self.get_serializer(
                instance, data={"plan_start_time": request.data.pop("plan_start_time")}, partial=True
            )
            serializer.is_valid(raise_exception=True)
            new_plan_start_time = serializer.validated_data["plan_start_time"]
            instance.modify_clock(new_plan_start_time)
        request.data["editor"] = request.user.username
        serializer = ClockedTaskPatchSerializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
