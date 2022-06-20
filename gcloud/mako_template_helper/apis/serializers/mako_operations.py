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

from rest_framework import serializers


class MakoOperationsResponseSerializers(serializers.Serializer):
    class MakoOperationsDataSerializers(serializers.Serializer):
        class OperationSerializer(serializers.Serializer):
            class OperatorSerializer(serializers.Serializer):
                name = serializers.CharField(help_text="操作符名称")
                type = serializers.CharField(help_text="操作符类型")

            class ParamSerializer(serializers.Serializer):
                name = serializers.CharField(help_text="参数名称")
                type = serializers.CharField(help_text="参数类型")

            name = serializers.CharField(help_text="操作名")
            operators = serializers.ListField(child=OperatorSerializer(help_text="操作符"))
            params = serializers.ListField(child=ParamSerializer(help_text="参数"))
            template = serializers.ListField(child=serializers.CharField(help_text="提示模板"))
            mako_template = serializers.CharField(help_text="MAKO 模板")

        operations = serializers.ListField(child=OperationSerializer(help_text="MAKO 操作"))

    result = serializers.BooleanField(help_text="请求是否成功")
    message = serializers.CharField(help_text="请求额外信息，result 为 false 时读取")
    data = MakoOperationsDataSerializers(help_text="响应数据")
