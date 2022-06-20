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


class VariableFieldExpainQuerySerializer(serializers.Serializer):
    bk_biz_id = serializers.IntegerField(required=False, help_text="业务 CC ID", min_value=0)


class FiledSerializer(serializers.Serializer):
    key = serializers.CharField(help_text="字段 key")
    type = serializers.CharField(help_text="字段类型")
    description = serializers.CharField(help_text="字段描述")


class VariableFieldExpainResponseSerializer(serializers.Serializer):
    class VariableFieldExpainDataSerializer(serializers.Serializer):
        class VariableFieldExpainSerializer(serializers.Serializer):
            tag = serializers.CharField(help_text="变量tag")
            fields = serializers.ListField(child=FiledSerializer(help_text="变量字段"))

        variable_field_explain = serializers.ListField(child=VariableFieldExpainSerializer(help_text="变量字段说明"))

    result = serializers.BooleanField(help_text="请求是否成功")
    message = serializers.CharField(help_text="请求额外信息，result 为 false 时读取")
    data = VariableFieldExpainDataSerializer(help_text="响应数据")
