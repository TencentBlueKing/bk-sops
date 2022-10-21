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
from gcloud.core.apis.drf.viewsets import IAMMixin
from gcloud.iam_auth import get_iam_client, res_factory, IAMMeta
from rest_framework import permissions


iam = get_iam_client()


class ClockedTaskPermissions(IAMMixin, permissions.BasePermission):
    actions = {
        "list": IAMMeta.PROJECT_VIEW_ACTION,
        "create": IAMMeta.FLOW_CREATE_CLOCKED_TASK_ACTION,
        "update": IAMMeta.CLOCKED_TASK_EDIT_ACTION,
        "partial_update": IAMMeta.CLOCKED_TASK_EDIT_ACTION,
        "retrieve": IAMMeta.CLOCKED_TASK_VIEW_ACTION,
        "destroy": IAMMeta.CLOCKED_TASK_DELETE_ACTION,
    }

    def has_permission(self, request, view):
        if view.action == "list":
            project_id = request.query_params.get("project_id")
            if project_id:
                self.iam_auth_check(
                    request,
                    action=self.actions[view.action],
                    resources=res_factory.resources_for_project(project_id),
                )
            else:
                self.iam_auth_check(
                    request,
                    action=IAMMeta.ADMIN_VIEW_ACTION,
                    resources=[],
                )
        elif view.action == "create":
            serializer = view.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)

            template_id = serializer.validated_data["template_id"]
            self.iam_auth_check(
                request,
                action=self.actions[view.action],
                resources=res_factory.resources_for_flow(template_id),
            )
        return True

    def has_object_permission(self, request, view, obj):
        if view.action in self.actions:
            self.iam_auth_check(
                request, action=self.actions[view.action], resources=res_factory.resources_for_clocked_task_obj(obj)
            )
        return True
