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

from rest_framework import permissions

from gcloud.iam_auth import IAMMeta, get_iam_client, res_factory

from iam import Subject, Action
from iam.shortcuts import allow_or_raise_auth_failed

iam = get_iam_client()


class ProjectConstantPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.action == "list":
            if "project_id" not in request.query_params:
                return False
            project_resources = res_factory.resources_for_project(request.query_params["project_id"])
            allow_or_raise_auth_failed(
                iam=iam,
                system=IAMMeta.SYSTEM_ID,
                subject=Subject("user", request.user.username),
                action=Action(IAMMeta.PROJECT_VIEW_ACTION),
                resources=project_resources,
            )

        elif view.action == "create":
            # let serializer to handle this
            if "project_id" not in request.data:
                return True

            project_resources = res_factory.resources_for_project(request.data["project_id"])
            allow_or_raise_auth_failed(
                iam=iam,
                system=IAMMeta.SYSTEM_ID,
                subject=Subject("user", request.user.username),
                action=Action(IAMMeta.PROJECT_VIEW_ACTION),
                resources=project_resources,
            )

        return True

    def has_object_permission(self, request, view, obj):
        project_resources = res_factory.resources_for_project(obj.project_id)
        allow_or_raise_auth_failed(
            iam=iam,
            system=IAMMeta.SYSTEM_ID,
            subject=Subject("user", request.user.username),
            action=Action(IAMMeta.PROJECT_EDIT_ACTION),
            resources=project_resources,
        )
        return True
