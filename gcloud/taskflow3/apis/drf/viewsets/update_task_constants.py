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
from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from iam import Subject, Action
from iam.shortcuts import allow_or_raise_auth_failed
from drf_yasg.utils import swagger_auto_schema

from gcloud.taskflow3.models import TaskFlowInstance
from gcloud.iam_auth import IAMMeta, get_iam_client, res_factory

iam = get_iam_client()


class RenderCurrentConstantsPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        task_id = view.kwargs["task_id"]
        task_resources = res_factory.resources_for_task(task_id)

        allow_or_raise_auth_failed(
            iam=iam,
            system=IAMMeta.SYSTEM_ID,
            subject=Subject("user", request.user.username),
            action=Action(IAMMeta.TASK_EDIT_ACTION),
            resources=task_resources,
        )

        return True


class UpdateTaskConstantsViewSerializer(serializers.Serializer):
    constants = serializers.DictField(help_text="需要修改的全局变量", required=True)

    def validate_constants(self, constants):
        if not constants:
            raise serializers.ValidationError("需要修改的全局变量不能为空")

        pre_render_constants = []
        hide_constants = []
        component_outputs = []
        for key, c in constants:
            if c.get("pre_render_mako", False):
                pre_render_constants.append(key)
            if c.get("show_type", "hide") != "show":
                hide_constants.append(key)
            if c.get("source_type") == "component_outputs":
                component_outputs.append(key)

        if pre_render_constants or hide_constants:
            raise serializers.ValidationError(
                """不支持修改以下变量
                预渲染变量: %s
                隐藏变量: %s
                组件输出: %s
                """
                % (pre_render_constants, hide_constants, component_outputs)
            )

        return constants


class UpdateTaskConstantsResponseSerializer(serializers.Serializer):
    result = serializers.BooleanField(help_text="请求是否成功")
    message = serializers.CharField(help_text="result=false返回错误的错误信息")
    data = serializers.CharField(help_text="更新说明")


class UpdateTaskConstantsView(APIView):
    @swagger_auto_schema(
        method="POST",
        operation_summary="修改未完成任务的全局变量值",
        responses={200: UpdateTaskConstantsResponseSerializer},
    )
    @action(methods=["POST"], detail=True)
    def post(self, request, task_id, format=None):
        serializers = UpdateTaskConstantsViewSerializer(data=request.data)
        serializers.is_valid(raise_exception=True)

        task = TaskFlowInstance.objects.filter(id=task_id).only("project_id", "engine_ver", "pipeline_instance")[0]
        set_result = task.set_task_constants(serializers.data["constants"])

        return Response(set_result)
