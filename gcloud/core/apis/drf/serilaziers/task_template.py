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

from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from gcloud.constants import DATETIME_FORMAT, TASK_CATEGORY
from gcloud.core.apis.drf.serilaziers.project import ProjectSerializer
from gcloud.core.apis.drf.serilaziers.template import BaseTemplateSerializer
from gcloud.core.models import Project
from gcloud.tasktmpl3.models import TaskTemplate


class BaseTaskTemplateSerializer(BaseTemplateSerializer):
    project = ProjectSerializer()


class TaskTemplateListSerializer(BaseTaskTemplateSerializer):
    name = serializers.CharField(read_only=True, help_text="模板名称")
    category_name = serializers.CharField(read_only=True, help_text="分类名称")
    creator_name = serializers.CharField(read_only=True, help_text="创建者名称")
    editor_name = serializers.CharField(read_only=True, help_text="编辑者名称")
    create_time = serializers.DateTimeField(help_text="创建时间", format=DATETIME_FORMAT)
    edit_time = serializers.DateTimeField(help_text="编辑时间", format=DATETIME_FORMAT)
    template_id = serializers.CharField(read_only=True, help_text="模板id")
    version = serializers.CharField(read_only=True, help_text="版本")
    subprocess_info = serializers.DictField(read_only=True, help_text="子流程信息")
    subprocess_has_update = serializers.BooleanField(read_only=True, help_text="子流程是否更新")
    has_subprocess = serializers.BooleanField(read_only=True, help_text="是否有子流程")
    description = serializers.CharField(read_only=True, help_text="流程描述", source="pipeline_template.description")

    class Meta:
        model = TaskTemplate
        fields = "__all__"


class TaskTemplateSerializer(TaskTemplateListSerializer):
    pipeline_tree = serializers.SerializerMethodField(read_only=True, help_text="pipeline_tree")

    def get_pipeline_tree(self, obj):
        return json.dumps(obj.pipeline_tree)


class TopCollectionTaskTemplateSerializer(TaskTemplateSerializer):
    is_collected = serializers.BooleanField(read_only=True, help_text="是否收藏")
    collection_id = serializers.IntegerField(read_only=True, help_text="收藏ID")


class UpdateDraftPipelineTreeSerializer(serializers.Serializer):
    name = serializers.CharField(required=True)
    template_labels = serializers.ListField(required=False)
    description = serializers.CharField(required=False, allow_null=True)
    pipeline_tree = serializers.JSONField(required=True)


class CreateTaskTemplateSerializer(BaseTaskTemplateSerializer):
    name = serializers.CharField(help_text="流程模板名称")
    category = serializers.ChoiceField(choices=TASK_CATEGORY, help_text="模板分类")
    time_out = serializers.IntegerField(help_text="超时时间", required=False)
    description = serializers.CharField(help_text="流程模板描述", allow_blank=True, required=False)
    executor_proxy = serializers.CharField(help_text="执行代理", allow_blank=True, required=False)
    template_labels = serializers.ListField(help_text="模板label", required=False)
    default_flow_type = serializers.CharField(help_text="默认流程类型")
    pipeline_tree = serializers.CharField()
    project = serializers.IntegerField(write_only=True)
    template_id = serializers.CharField(help_text="模板ID", source="id", read_only=True)

    def validate_project(self, value):
        try:
            return Project.objects.get(id=value)
        except Project.DoesNotExist:
            raise serializers.ValidationError(_("project不存在"))

    class Meta:
        model = TaskTemplate
        fields = [
            "name",
            "category",
            "time_out",
            "description",
            "executor_proxy",
            "template_labels",
            "default_flow_type",
            "notify_type",
            "notify_receivers",
            "pipeline_tree",
            "project",
            "template_id",
        ]


class UpdateTaskTemplateSerializer(BaseTemplateSerializer):
    category = serializers.ChoiceField(choices=TASK_CATEGORY, help_text="模板分类")
    time_out = serializers.IntegerField(help_text="超时时间", required=False)
    executor_proxy = serializers.CharField(help_text="执行代理", allow_blank=True, required=False)
    default_flow_type = serializers.CharField(help_text="默认流程类型")

    class Meta:
        model = TaskTemplate
        fields = "__all__"


class ProjectInfoQuerySerializer(serializers.Serializer):
    project_id = serializers.IntegerField(help_text="项目ID")


class ProjectFilterQuerySerializer(serializers.Serializer):
    project__id = serializers.IntegerField(help_text="项目ID")
