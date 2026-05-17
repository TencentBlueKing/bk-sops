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


class PluginGatewayRunCreateSerializer(serializers.Serializer):
    source_key = serializers.CharField(max_length=64)
    plugin_id = serializers.CharField(max_length=128)
    plugin_version = serializers.CharField(max_length=64)
    client_request_id = serializers.CharField(max_length=128)
    callback_url = serializers.URLField(max_length=512)
    callback_token = serializers.CharField(max_length=512)
    inputs = serializers.DictField(required=False, default=dict)
    project_id = serializers.IntegerField(required=False)
    operator = serializers.CharField(max_length=128, required=False)


class PluginGatewayRunStatusQuerySerializer(serializers.Serializer):
    task_tag = serializers.CharField(max_length=64)
