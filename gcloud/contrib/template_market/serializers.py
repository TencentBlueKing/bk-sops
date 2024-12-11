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
import logging
from rest_framework import serializers

from gcloud.constants import DATETIME_FORMAT
from gcloud.contrib.template_market.models import TemplateSharedRecord


class TemplatePreviewSerializer(serializers.Serializer):
    name = serializers.CharField(read_only=True, help_text="模板名称")
    pipeline_tree = serializers.SerializerMethodField(read_only=True, help_text="pipeline_tree")

    def get_pipeline_tree(self, obj):
        return json.dumps(obj.pipeline_tree)


class TemplateProjectBaseSerializer(serializers.Serializer):
    template_id = serializers.CharField(required=True, help_text="模板id")
    project_id = serializers.CharField(required=True, help_text="项目id")


class TemplateSharedRecordSerializer(serializers.ModelSerializer):
    project_id = serializers.CharField(required=True, max_length=32, help_text="项目id")
    templates = serializers.ListField(required=True, help_text="关联的模板列表")
    creator = serializers.CharField(required=False, max_length=32, help_text="创建者")
    create_at = serializers.DateTimeField(required=False, help_text="创建时间", format=DATETIME_FORMAT)
    update_at = serializers.DateTimeField(required=False, help_text="更新时间", format=DATETIME_FORMAT)
    extra_info = serializers.JSONField(required=False, allow_null=True, help_text="额外信息")
    id = serializers.IntegerField(required=False, help_text="共享实例id")
    name = serializers.CharField(required=True, help_text="共享名称")
    code = serializers.CharField(required=True, help_text="共享标识")
    category = serializers.CharField(required=True, help_text="共享分类")
    risk_level = serializers.IntegerField(required=True, help_text="风险级别")
    usage_id = serializers.IntegerField(required=True, help_text="使用说明id")
    labels = serializers.ListField(child=serializers.IntegerField(), required=True, help_text="共享标签列表")
    usage_content = serializers.JSONField(required=True, help_text="使用说明")

    class Meta:
        model = TemplateSharedRecord
        fields = [
            "project_id",
            "templates",
            "creator",
            "create_at",
            "update_at",
            "extra_info",
            "labels",
            "usage_content",
            "id",
            "name",
            "code",
            "category",
            "risk_level",
            "usage_id",
        ]

    def convert_templates(self, templates):
        return [template.get("id") for template in templates]

    def create(self, validated_data):
        try:
            validated_data["templates"] = self.convert_templates(validated_data["templates"])
            return TemplateSharedRecord.objects.create(
                scene_shared_id=validated_data["id"],
                project_id=validated_data["project_id"],
                templates=validated_data["templates"],
                creator=validated_data["creator"],
                extra_info=validated_data["extra_info"],
            )
        except Exception:
            logging.exception("Failed to create model sharing record")
            raise Exception("Failed to create model sharing record")

    def update(self, instance, validated_data):
        try:
            validated_data["templates"] = self.convert_templates(validated_data["templates"])
            instance.project_id = validated_data["project_id"]
            instance.templates = validated_data["templates"]
            instance.creator = validated_data["creator"]
            instance.extra_info = validated_data["extra_info"]
            instance.save()
        except Exception:
            logging.exception("Failed to update model sharing record")
            raise Exception("Failed to update model sharing record")
