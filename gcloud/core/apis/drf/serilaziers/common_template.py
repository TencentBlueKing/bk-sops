# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2022 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
import json
from rest_framework import serializers

from gcloud.utils.drf.serializer import ReadWriteSerializerMethodField
from gcloud.constants import TASK_CATEGORY, DATETIME_FORMAT
from gcloud.common_template.models import CommonTemplate
from gcloud.core.apis.drf.serilaziers.template import BaseTemplateSerializer


class CommonTemplateSerializer(BaseTemplateSerializer):
    category_name = serializers.CharField(help_text="分类名称")
    create_time = serializers.DateTimeField(help_text="创建时间", format=DATETIME_FORMAT)
    creator_name = serializers.CharField(help_text="创建者名")
    description = serializers.CharField(help_text="公共流程描述", source="pipeline_template.description")
    editor_name = serializers.CharField(help_text="编辑者名称")
    edit_time = serializers.DateTimeField(help_text="编辑时间", format=DATETIME_FORMAT)
    has_subprocess = serializers.BooleanField(help_text="是否有子流程")
    name = serializers.CharField(help_text="公共流程名称")
    pipeline_template = serializers.IntegerField(help_text="pipeline模板ID", source="pipeline_template.id")
    subprocess_has_update = serializers.BooleanField(help_text="子流程是否更新")
    template_id = serializers.IntegerField(help_text="流程ID")
    version = serializers.CharField(help_text="流程版本")
    pipeline_tree = serializers.SerializerMethodField(read_only=True, help_text="pipeline_tree")

    def get_pipeline_tree(self, obj):
        try:
            if not getattr(obj, "pipeline_tree") or not obj.pipeline_tree:
                return json.dumps(dict())
            return json.dumps(obj.pipeline_tree)
        except CommonTemplate.DoesNotExist:
            return json.dumps(dict())

    class Meta:
        model = CommonTemplate
        fields = "__all__"


class CreateCommonTemplateSerializer(BaseTemplateSerializer):
    name = serializers.CharField(help_text="流程模板名称")
    category = serializers.ChoiceField(choices=TASK_CATEGORY, help_text="模板分类")
    time_out = serializers.IntegerField(help_text="超时时间", required=False)
    description = serializers.CharField(help_text="流程模板描述", allow_blank=True, required=False)
    notify_type = ReadWriteSerializerMethodField(help_text="通知类型")
    notify_receivers = ReadWriteSerializerMethodField(help_text="通知人列表")
    pipeline_tree = serializers.CharField()
    id = serializers.IntegerField(help_text="公共流程ID", read_only=True)
    creator_name = serializers.CharField(read_only=True, help_text="创建者名")
    category_name = serializers.CharField(read_only=True, help_text="分类名称")
    editor_name = serializers.CharField(read_only=True, help_text="编辑者名")
    create_time = serializers.DateTimeField(read_only=True, help_text="创建时间", format=DATETIME_FORMAT)
    edit_time = serializers.DateTimeField(read_only=True, help_text="编辑时间", format=DATETIME_FORMAT)
    has_subprocess = serializers.BooleanField(read_only=True, help_text="是否有子流程")
    subprocess_has_update = serializers.BooleanField(help_text="子流程是否更新", read_only=True)
    template_id = serializers.IntegerField(help_text="流程ID", read_only=True)
    version = serializers.CharField(help_text="流程版本", read_only=True)
    pipeline_template = serializers.IntegerField(
        help_text="pipeline模板ID", source="pipeline_template.id", read_only=True
    )

    class Meta:
        model = CommonTemplate
        fields = [
            "id",
            "name",
            "category",
            "time_out",
            "description",
            "notify_type",
            "notify_receivers",
            "pipeline_tree",
            "creator_name",
            "category_name",
            "editor_name",
            "create_time",
            "edit_time",
            "has_subprocess",
            "subprocess_has_update",
            "template_id",
            "version",
            "pipeline_template",
        ]
