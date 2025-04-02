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

from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import permissions
from drf_yasg.utils import swagger_auto_schema
from pipeline.core.data.library import VariableLibrary

from pipeline_plugins.variables.base import SelfExplainVariable
from ..serilaziers.variable_field_explain import (
    VariableFieldExpainQuerySerializer,
    VariableFieldExpainResponseSerializer,
)


class VariableFieldExplainView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        method="GET",
        operation_summary="获取所有变量及其字段的描述信息",
        query_serializer=VariableFieldExpainQuerySerializer,
        responses={200: VariableFieldExpainResponseSerializer},
    )
    @action(methods=["GET"], detail=False)
    def get(self, request, format=None):
        serializer = VariableFieldExpainQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        validated_data["tenant_id"] = request.user.tenant_id
        data = {
            "variable_field_explain": [
                var_cls.self_explain(**validated_data)
                for var_cls in VariableLibrary.variables.values()
                if issubclass(var_cls, SelfExplainVariable)
            ]
        }
        return Response({"result": True, "message": "success", "data": data})
