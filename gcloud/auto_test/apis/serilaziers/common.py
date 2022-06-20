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


class IdsListSerializer(serializers.Serializer):
    """用于一些批量操作参数序列化使用"""

    ids_list = serializers.ListField(help_text="ID列表", child=serializers.IntegerField())


class BatchDeleteSerialzer(serializers.Serializer):
    pass


class AutoTestTokenSerialzer(serializers.Serializer):
    key = serializers.CharField(help_text="加密的key")
    expire = serializers.IntegerField(help_text="超时时间")
