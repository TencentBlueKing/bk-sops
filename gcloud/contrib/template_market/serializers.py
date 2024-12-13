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
import json

from rest_framework import serializers


class TemplatePreviewSerializer(serializers.Serializer):
    name = serializers.CharField(read_only=True, help_text="模板名称")
    pipeline_tree = serializers.SerializerMethodField(read_only=True, help_text="pipeline_tree")

    def get_pipeline_tree(self, obj):
        # todo 节点信息防护
        return json.dumps(obj.pipeline_tree)


class TemplateProjectBaseSerializer(serializers.Serializer):
    template_id = serializers.CharField(required=True, help_text="模板id")
    project_id = serializers.CharField(required=True, help_text="项目id")


class TemplateSharedRecordSerializer(serializers.Serializer):
    project_id = serializers.CharField(required=True, max_length=32, help_text="项目id")
    template_ids = serializers.ListField(required=True, help_text="关联的模板列表")
    creator = serializers.CharField(required=True, max_length=32, help_text="创建者")
    extra_info = serializers.JSONField(required=False, allow_null=True, help_text="额外信息")
    name = serializers.CharField(required=True, help_text="共享名称")
    code = serializers.CharField(required=True, help_text="共享标识")
    category = serializers.CharField(required=True, help_text="共享分类")
    risk_level = serializers.IntegerField(required=True, help_text="风险级别")
    usage_id = serializers.IntegerField(required=True, help_text="使用说明id")
    labels = serializers.ListField(child=serializers.IntegerField(), required=True, help_text="共享标签列表")
    usage_content = serializers.JSONField(required=True, help_text="使用说明")
