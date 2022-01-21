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
specific lan
"""

import logging
from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework import permissions
from rest_framework.response import Response

from gcloud.constants import PROJECT
from drf_yasg.utils import swagger_auto_schema

from pipeline_web.preview import preview_template_tree_with_schemes

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
        try:
            data = preview_template_tree_with_schemes(**serializer.data)
        except Exception as e:
            err_msg = "preview_template_tree_with_schemes fail: {}".format(e)
            logger.exception(err_msg)
            return Response({"result": False, "message": err_msg, "data": {}})

        return Response({"result": True, "data": data, "message": "success"})
