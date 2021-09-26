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

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions, status
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response

from gcloud.clocked_task.models import ClockedTask
from gcloud.clocked_task.permissions import ClockedTaskPermissions
from gcloud.clocked_task.serializer import ClockedTaskSerializer
from gcloud.core.apis.drf.viewsets import ApiMixin, IAMMixin
from gcloud.iam_auth import get_iam_client, IAMMeta
from gcloud.iam_auth.resource_helpers.clocked_task import ClockedTaskResourceHelper

iam = get_iam_client()


class ClockedTaskViewSet(ApiMixin, IAMMixin, viewsets.ModelViewSet):
    queryset = ClockedTask.objects.all()
    permission_classes = [permissions.IsAuthenticated, ClockedTaskPermissions]
    serializer_class = ClockedTaskSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        "creator": ["exact"],
        "plan_start_time": ["gte", "lte"],
        "task_name": ["exact", "icontains", "contains"],
        "project_id": ["exact"],
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

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)

        serializer = self.get_serializer(page if page is not None else queryset, many=True)
        deserialized_instances = serializer.data
        auth_actions = self.iam_get_instances_auth_actions(request, list(queryset))
        if auth_actions:
            for deserialized_instance in deserialized_instances:
                deserialized_instance["auth_actions"] = auth_actions[deserialized_instance["id"]]

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
        if "plan_start_time" in request.data:
            instance = self.get_object()
            serializer = self.get_serializer(
                instance, data={"plan_start_time": request.data.pop("plan_start_time")}, partial=True
            )
            serializer.is_valid(raise_exception=True)
            validated_data = serializer.validated_data
            new_plan_start_time = validated_data["plan_start_time"]
            instance.modify_clock(new_plan_start_time)
        kwargs["partial"] = True
        return super().update(request, *args, **kwargs)
