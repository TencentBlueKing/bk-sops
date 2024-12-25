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

from gcloud.constants import PROJECT
from gcloud.taskflow3.models import TaskTemplate
from pipeline_web.constants import PWE

TEMPLATE_OPERATE_MAX_NUMBER = 10


class TemplatePreviewSerializer(serializers.Serializer):
    name = serializers.CharField(read_only=True, help_text="模板名称")
    pipeline_tree = serializers.SerializerMethodField(read_only=True, help_text="pipeline_tree")

    def get_pipeline_tree(self, obj):
        # todo 节点信息防护
        return json.dumps(obj.pipeline_tree)


class TemplateProjectBaseSerializer(serializers.Serializer):
    template_id = serializers.CharField(required=True, help_text="模板id")
    project_id = serializers.CharField(required=True, help_text="项目id")
    template_source = serializers.CharField(help_text="流程模版类型", default=PROJECT)


class SceneLabelSerializer(serializers.Serializer):
    name = serializers.CharField(required=True, help_text="标签名称")
    code = serializers.CharField(required=True, help_text="场景标签英文标识")


class FileUploadAddrSerializer(serializers.Serializer):
    scene_type = serializers.CharField(required=True, help_text="场景类型")
    scene_code = serializers.CharField(required=True, help_text="场景标识")
    file_name = serializers.CharField(required=True, help_text="文件名称")


class TemplateSharedRecordSerializer(serializers.Serializer):
    project_code = serializers.CharField(required=True, max_length=32, help_text="项目id")
    templates = serializers.ListField(required=True, help_text="关联的模板列表")
    name = serializers.CharField(required=True, help_text="共享名称")
    category = serializers.CharField(required=True, help_text="共享分类")
    risk_level = serializers.IntegerField(required=True, help_text="风险级别")
    usage_id = serializers.IntegerField(required=False, help_text="使用说明id")
    labels = serializers.ListField(child=serializers.IntegerField(), required=True, help_text="共享标签列表")
    usage_content = serializers.JSONField(required=True, help_text="使用说明")

    def validate_template_ids(self, value):
        if not self.check_template_count_threshold(value):
            raise serializers.ValidationError("The number of processes in the selected template exceeds the limit.")

        return value

    def check_template_count_threshold(self, template_id_list):
        if len(template_id_list) > TEMPLATE_OPERATE_MAX_NUMBER:
            return False

        templates = TaskTemplate.objects.filter(id__in=template_id_list).select_related("pipeline_template")

        acts = [act for tmpl in templates for act in tmpl.pipeline_template.data.get(PWE.activities, {}).values()]
        # TODO: 目前只做了一层的数量统计
        count = sum(act["type"] == PWE.SubProcess for act in acts)

        return len(template_id_list) + count < TEMPLATE_OPERATE_MAX_NUMBER
