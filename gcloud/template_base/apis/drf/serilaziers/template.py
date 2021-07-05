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


class TemplateIdsSerializer(serializers.Serializer):
    """用于一些批量操作参数序列化使用"""

    template_ids = serializers.ListField(help_text="流程ID列表", child=serializers.IntegerField())


class BatchOperationSerializer(serializers.Serializer):
    success = serializers.ListField(help_text="成功流程ID列表", child=serializers.IntegerField())
    fail = serializers.ListField(help_text="失败流程ID列表", child=serializers.IntegerField())


class ReferenceSerializer(serializers.Serializer):
    name = serializers.CharField(help_text="引用对象名称")
    id = serializers.IntegerField(help_text="引用对象ID")


class ReferencesSerializer(serializers.Serializer):
    template = ReferenceSerializer(help_text="引用其他流程信息")
    appmaker = ReferenceSerializer(help_text="引用轻应用信息")


class TemplateReferencesSerializer(serializers.Serializer):
    template_id = ReferenceSerializer(help_text="对应流程引用其他对象情况")


class BatchDeleteSerialzer(BatchOperationSerializer):
    references = TemplateReferencesSerializer(help_text="删除失败流程引用其他对象信息")
