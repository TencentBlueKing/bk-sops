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
from rest_framework import permissions
from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from iam import Subject, Action
from iam.shortcuts import allow_or_raise_auth_failed
from drf_yasg.utils import swagger_auto_schema
from gcloud.contrib.operate_record.constants import OperateType, OperateSource

from gcloud.taskflow3.models import TaskFlowInstance
from gcloud.iam_auth import IAMMeta, get_iam_client, res_factory
from gcloud.contrib.operate_record.models import TaskOperateRecord
from gcloud.contrib.operate_record.utils import extract_extra_info

iam = get_iam_client()


class UpdateTaskConstantsPermission(permissions.BasePermission):
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
    meta_constants = serializers.DictField(help_text="需要修改的全局中的元变量元信息", required=False, default={})


class UpdateTaskConstantsResponseSerializer(serializers.Serializer):
    result = serializers.BooleanField(help_text="请求是否成功")
    message = serializers.CharField(help_text="result=false返回错误的错误信息")
    data = serializers.CharField(help_text="更新说明")


class UpdateTaskConstantsView(APIView):

    permission_classes = [permissions.IsAuthenticated, UpdateTaskConstantsPermission]

    @swagger_auto_schema(
        method="POST",
        operation_summary="修改任务的全局变量值",
        request_body=UpdateTaskConstantsViewSerializer,
        responses={200: UpdateTaskConstantsResponseSerializer},
    )
    @action(methods=["POST"], detail=True)
    def post(self, request, task_id, format=None):
        serializers = UpdateTaskConstantsViewSerializer(data=request.data)
        serializers.is_valid(raise_exception=True)

        task = TaskFlowInstance.objects.filter(id=task_id).only("project_id", "engine_ver", "pipeline_instance").first()
        set_result = task.set_task_constants(serializers.data["constants"], serializers.data["meta_constants"])

        if set_result["result"]:
            constants = task.pipeline_instance.execution_data.get("constants")
            extra_info = extract_extra_info(
                constants,
                keys=request.data.get("modified_constant_keys") if "modified_constant_keys" in request.data else None)

            TaskOperateRecord.objects.create(
                operator=request.user.username,
                operate_type=OperateType.update.name,
                operate_source=OperateSource.app.name,
                instance_id=task_id,
                project_id=task.project_id,
                extra_info=extra_info,
            )

        return Response(set_result)
