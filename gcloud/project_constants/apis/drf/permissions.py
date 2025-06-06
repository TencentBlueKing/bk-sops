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

from iam import Action, Subject
from iam.shortcuts import allow_or_raise_auth_failed
from rest_framework import permissions

from gcloud.iam_auth import IAMMeta, get_iam_client, res_factory

from .serializers import ProjectConstantsListPermissionSerializer


class ProjectConstantPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        tenant_id = request.user.tenant_id
        iam = get_iam_client(tenant_id)
        if view.action == "list":
            serializer = ProjectConstantsListPermissionSerializer(data=request.query_params)
            serializer.is_valid(raise_exception=True)

            project_resources = res_factory.resources_for_project(serializer.validated_data["project_id"], tenant_id)
            allow_or_raise_auth_failed(
                iam=iam,
                system=IAMMeta.SYSTEM_ID,
                subject=Subject("user", request.user.username),
                action=Action(IAMMeta.PROJECT_VIEW_ACTION),
                resources=project_resources,
            )

        elif view.action == "create":
            # let serializer to handle this
            serializer = view.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)

            project_resources = res_factory.resources_for_project(serializer.validated_data["project_id"], tenant_id)
            allow_or_raise_auth_failed(
                iam=iam,
                system=IAMMeta.SYSTEM_ID,
                subject=Subject("user", request.user.username),
                action=Action(IAMMeta.PROJECT_EDIT_ACTION),
                resources=project_resources,
            )

        return True

    def has_object_permission(self, request, view, obj):
        tenant_id = request.user.tenant_id
        iam = get_iam_client(tenant_id)
        project_resources = res_factory.resources_for_project(obj.project_id, tenant_id)
        allow_or_raise_auth_failed(
            iam=iam,
            system=IAMMeta.SYSTEM_ID,
            subject=Subject("user", request.user.username),
            action=Action(IAMMeta.PROJECT_EDIT_ACTION),
            resources=project_resources,
        )
        return True
