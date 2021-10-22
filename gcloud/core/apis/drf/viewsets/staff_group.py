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
from rest_framework import permissions, mixins, viewsets
from rest_framework.response import Response

from gcloud.core.models import StaffGroupSet
from gcloud.core.apis.drf.serilaziers.staff_group import StaffGroupSetSerializer, ListSerializer
from gcloud.core.apis.drf.viewsets.utils import ApiMixin, IAMMixin
from gcloud.iam_auth import IAMMeta, res_factory


class StaffGroupSetViewSet(
    ApiMixin,
    IAMMixin,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = StaffGroupSet.objects.filter(is_deleted=False).order_by("-id")
    serializer_class = StaffGroupSetSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_data(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data

    def list(self, request, *args, **kwargs):
        serializer = ListSerializer(data=self.request.query_params)
        serializer.is_valid(raise_exception=True)
        project_id = serializer.validated_data["project_id"]
        self.iam_auth_check(
            request, action=IAMMeta.PROJECT_VIEW_ACTION, resources=res_factory.resources_for_project(project_id)
        )
        queryset = self.get_queryset().filter(project_id=project_id)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        validated_data = self.get_serializer_data(request)

        staff_group_obj = StaffGroupSet.objects.create(**validated_data)
        self.iam_auth_check(
            request,
            action=IAMMeta.PROJECT_EDIT_ACTION,
            resources=res_factory.resources_for_project(staff_group_obj.project_id),
        )
        serializer = self.serializer_class(instance=staff_group_obj)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        validated_data = self.get_serializer_data(request)
        self.iam_auth_check(
            request,
            action=IAMMeta.PROJECT_EDIT_ACTION,
            resources=res_factory.resources_for_project(validated_data.get("project_id")),
        )

        instance = self.get_object()
        instance.name = validated_data.get("name")
        instance.members = validated_data.get("members")
        instance.save()
        serializer = self.serializer_class(instance=instance)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.iam_auth_check(
            request,
            action=IAMMeta.PROJECT_EDIT_ACTION,
            resources=res_factory.resources_for_project(instance.project_id),
        )
        instance.is_deleted = True
        instance.save()
        serializer = self.serializer_class(instance=instance)
        return Response(serializer.data)
