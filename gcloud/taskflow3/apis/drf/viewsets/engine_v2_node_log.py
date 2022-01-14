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

from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import permissions
from iam import Subject, Action
from iam.shortcuts import allow_or_raise_auth_failed
from drf_yasg.utils import swagger_auto_schema
from pipeline.eri.runtime import BambooDjangoRuntime

from gcloud.iam_auth import IAMMeta, get_iam_client, res_factory
from gcloud.utils.handlers import handle_plain_log

iam = get_iam_client()


class EngineV2NodeLogViewPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        task_id = view.kwargs["task_id"]
        task_resources = res_factory.resources_for_task(task_id)

        allow_or_raise_auth_failed(
            iam=iam,
            system=IAMMeta.SYSTEM_ID,
            subject=Subject("user", request.user.username),
            action=Action(IAMMeta.TASK_VIEW_ACTION),
            resources=task_resources,
        )

        return True


class EngineV2NodeLogViewResponse(serializers.Serializer):
    data = serializers.CharField(read_only=True, help_text="日志内容")
    message = serializers.CharField(read_only=True, help_text="接口错误信息")
    result = serializers.BooleanField(read_only=True, help_text="请求是否成功")


class EngineV2NodeLogView(APIView):
    permission_classes = [permissions.IsAuthenticated, EngineV2NodeLogViewPermission]

    @swagger_auto_schema(
        method="GET",
        operation_summary="获取某个节点的执行日志",
        responses={200: EngineV2NodeLogViewResponse},
    )
    @action(methods=["GET"], detail=True)
    def get(self, request, project_id, task_id, node_id, version):
        runtime = BambooDjangoRuntime()
        logs = handle_plain_log(runtime.get_plain_log_for_node(node_id=node_id, version=version))

        return Response({"result": True, "message": "success", "data": logs})
