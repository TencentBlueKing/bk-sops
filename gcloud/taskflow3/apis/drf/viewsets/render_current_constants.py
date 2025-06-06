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

from drf_yasg.utils import swagger_auto_schema
from iam import Action, Subject
from iam.shortcuts import allow_or_raise_auth_failed
from rest_framework import permissions, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from gcloud.iam_auth import IAMMeta, get_iam_client, res_factory
from gcloud.taskflow3.domains.dispatchers.task import TaskCommandDispatcher
from gcloud.taskflow3.models import TaskFlowInstance
from gcloud.utils.json import safe_for_json


class RenderCurrentConstantsPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        task_id = view.kwargs["task_id"]
        tenant_id = request.user.tenant_id
        iam = get_iam_client(tenant_id)
        task_resources = res_factory.resources_for_task(task_id, tenant_id)

        allow_or_raise_auth_failed(
            iam=iam,
            system=IAMMeta.SYSTEM_ID,
            subject=Subject("user", request.user.username),
            action=Action(IAMMeta.TASK_VIEW_ACTION),
            resources=task_resources,
        )

        return True


class RenderCurrentConstantsViewResponse(serializers.Serializer):
    key = serializers.CharField(read_only=True, help_text="变量KEY")
    value = serializers.CharField(read_only=True, help_text="变量值")


class RenderCurrentConstantsView(APIView):

    permission_classes = [permissions.IsAuthenticated, RenderCurrentConstantsPermission]

    @swagger_auto_schema(
        method="GET",
        operation_summary="获取某个任务所有全局变量当前渲染后的值",
        responses={200: RenderCurrentConstantsViewResponse},
    )
    @action(methods=["GET"], detail=True)
    def get(self, request, task_id, format=None):
        # fetch require task data
        task = TaskFlowInstance.objects.filter(id=task_id).only("id", "engine_ver", "pipeline_instance", "project_id")[
            0
        ]

        # dispatch get constants command
        resp_data = TaskCommandDispatcher(
            engine_ver=task.engine_ver,
            taskflow_id=task.id,
            pipeline_instance=task.pipeline_instance,
            project_id=task.project_id,
        ).render_current_constants()

        if resp_data["result"]:
            for var in resp_data["data"]:
                if safe_for_json(var["value"]):
                    continue
                var["value"] = str(var["value"].__dict__) if hasattr(var["value"], "__dict__") else str(var["value"])

        return Response(resp_data)
