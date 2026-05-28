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
from django.http import QueryDict
from iam import Action, Subject
from iam.shortcuts import allow_or_raise_auth_failed
from rest_framework import mixins, permissions, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from gcloud.core.apis.drf.serilaziers import ResourceConfigSerializer
from gcloud.core.apis.drf.viewsets.utils import ApiMixin
from gcloud.core.models import ResourceConfig
from gcloud.iam_auth import IAMMeta, get_iam_client, res_factory

iam = get_iam_client()


class ResourceConfigPermission(permissions.BasePermission):
    """资源配置权限校验

    - list/create 通过请求参数中的 project_id 校验项目级权限；
    - retrieve/update/partial_update 通过对象自身的 project_id 校验，避免攻击者借助
      请求参数中的 project_id 越权读取/修改其它项目的资源配置（IDOR）；
    - 写操作要求 project_edit，而非 project_view。
    """

    @staticmethod
    def _auth_project(request, action, project_id):
        if not project_id:
            raise PermissionDenied
        allow_or_raise_auth_failed(
            iam=iam,
            system=IAMMeta.SYSTEM_ID,
            subject=Subject("user", request.user.username),
            action=Action(action),
            resources=res_factory.resources_for_project(project_id),
        )

    def has_permission(self, request, view):
        if view.action == "list":
            project_id = request.query_params.get("project_id")
            self._auth_project(request, IAMMeta.PROJECT_VIEW_ACTION, project_id)
        elif view.action == "create":
            project_id = request.data.get("project_id")
            self._auth_project(request, IAMMeta.PROJECT_EDIT_ACTION, project_id)
        # retrieve/update/partial_update 交由 has_object_permission 基于对象校验
        return True

    def has_object_permission(self, request, view, obj):
        action = IAMMeta.PROJECT_VIEW_ACTION if view.action == "retrieve" else IAMMeta.PROJECT_EDIT_ACTION
        self._auth_project(request, action, obj.project_id)
        return True


class ResourceConfigViewSet(
    ApiMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = ResourceConfig.objects.all().order_by("-id")
    serializer_class = ResourceConfigSerializer
    permission_classes = [permissions.IsAuthenticated, ResourceConfigPermission]

    def list(self, request, *args, **kwargs):
        project_id = request.query_params.get("project_id")
        config_type = request.query_params.get("config_type")
        queryset = self.get_queryset().filter(project_id=project_id, config_type=config_type)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        if isinstance(request.data, QueryDict):
            request.data._mutable = True
        request.data.update({"creator": request.user.username})
        return super(ResourceConfigViewSet, self).create(request, *args, **kwargs)
