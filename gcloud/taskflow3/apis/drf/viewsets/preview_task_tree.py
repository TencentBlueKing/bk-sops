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
specific lan
"""

import logging
from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework import permissions
from rest_framework.response import Response

from gcloud.common_template.models import CommonTemplate
from gcloud.constants import PROJECT
from drf_yasg.utils import swagger_auto_schema

from gcloud.tasktmpl3.models import TaskTemplate
from pipeline_web.preview import preview_template_tree_with_schemes
from django.utils.translation import ugettext_lazy as _

logger = logging.getLogger("root")


class PreviewTaskTreeWithSchemesSerializer(serializers.Serializer):
    project_id = serializers.IntegerField(help_text="项目ID", required=False)
    template_id = serializers.CharField(help_text="流程模版ID")
    version = serializers.CharField(help_text="流程模版版本", allow_blank=True)
    template_source = serializers.CharField(help_text="流程模版类型", default=PROJECT)
    scheme_id_list = serializers.ListField(help_text="执行方案ID列表")

    def validate_template_source(self, template_source):
        if template_source == PROJECT and "project_id" not in self.initial_data:
            raise serializers.ValidationError("预览项目流程模版必须传入项目ID")

        return template_source


class PreviewTaskTreeResponseSerializer(serializers.Serializer):
    result = serializers.BooleanField(help_text="请求是否成功")
    message = serializers.CharField(help_text="result=false返回错误的错误信息")
    data = serializers.DictField(help_text="返回的pipeline_tree数据")


class PreviewTaskTreeWithSchemesView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        method="POST",
        operation_summary="根据执行方案列表预览任务流程",
        request_body=PreviewTaskTreeWithSchemesSerializer,
        responses={200: PreviewTaskTreeResponseSerializer},
    )
    @action(methods=["POST"], detail=False)
    def post(self, request):
        serializer = PreviewTaskTreeWithSchemesSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        project_id = serializer.data.get("project_id")
        template_id = serializer.data["template_id"]
        version = serializer.data["version"]
        template_source = serializer.data["template_source"]
        scheme_id_list = serializer.data["scheme_id_list"]

        try:
            if template_source == PROJECT:
                template = TaskTemplate.objects.get(pk=template_id, is_deleted=False, project_id=project_id)
            else:
                template = CommonTemplate.objects.get(pk=template_id, is_deleted=False)
        except TaskTemplate.DoesNotExist:
            message = _(f"请求任务数据失败: 任务关联的流程[ID: {template_id}]已不存在, 项目[ID: {project_id}] 请检查 | preview_task_tree")
            logger.error(message)
            return Response({"result": False, "message": message, "data": {}})
        except CommonTemplate.DoesNotExist:
            err_msg = "[[preview_task_tree_with_schemes]] common template[{}] doesn't exist".format(template_id)
            logger.exception(err_msg)
            return Response({"result": False, "message": err_msg, "data": {}})

        try:
            data = preview_template_tree_with_schemes(template, version, scheme_id_list)
        except Exception as e:
            message = _(f"任务数据请求失败: 获取带执行方案流程树数据失败, 错误信息: {e}, 请重试. 如多次失败可联系管理员处理 | preview_task_tree")
            logger.exception(message)
            return Response({"result": False, "message": message, "data": {}})

        return Response({"result": True, "data": data, "message": "success"})
