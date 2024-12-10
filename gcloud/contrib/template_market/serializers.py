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

from gcloud.constants import DATETIME_FORMAT
from gcloud.contrib.template_market.models import TemplateSharedRecord
from gcloud.tasktmpl3.models import TaskTemplate


class TemplatePreviewSerializer(serializers.ModelSerializer):
    name = serializers.CharField(read_only=True, help_text="模板名称")
    pipeline_tree = serializers.SerializerMethodField(read_only=True, help_text="pipeline_tree")

    def get_pipeline_tree(self, obj):
        return json.dumps(obj.pipeline_tree)

    class Meta:
        model = TaskTemplate
        fields = ["name", "pipeline_tree"]


class TemplateSharedRecordSerializer(serializers.Serializer):
    template_id = serializers.CharField(required=True, help_text="模板id")
    project_id = serializers.CharField(required=True, help_text="项目id")
    name = serializers.CharField(required=True, help_text="场景名称")
    code = serializers.CharField(required=True, help_text="场景标识")
    category = serializers.CharField(required=True, help_text="场景分类")
    risk_level = serializers.IntegerField(required=True, help_text="风险级别")
    labels = serializers.ListField(child=serializers.IntegerField(), required=True, help_text="场景标签列表")
    usage_content = serializers.CharField(required=True, help_text="使用说明")
    creator = serializers.CharField(required=False, max_length=32, help_text="创建者")
    create_at = serializers.DateTimeField(required=False, help_text="创建时间", format=DATETIME_FORMAT)
    extra_info = serializers.JSONField(required=False, allow_null=True, help_text="额外信息")

    def create(self, validated_data):
        instance = TemplateSharedRecord.objects.create(
            project_id=validated_data["project_id"],
            template_id=validated_data["template_id"],
            creator=validated_data.get("creator", ""),
            extra_info=validated_data.get("extra_info"),
        )
        return instance

    class Meta:
        model = TemplateSharedRecord
        fields = [
            "project_id",
            "template_id",
            "creator",
            "create_at",
            "extra_info",
            "name",
            "code",
            "category",
            "risk_level",
            "labels",
            "usage_content",
        ]
