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
from gcloud.constants import PROJECT


class TemplateParamsSerializer(serializers.Serializer):
    id = serializers.IntegerField(help_text="流程模版ID")
    version = serializers.CharField(help_text="流程模版版本", allow_blank=True)
    template_source = serializers.CharField(help_text="流程模版类型", default=PROJECT)
    scheme_id_list = serializers.ListField(help_text="执行方案ID列表")


class BatchTemplateFormWithSchemesSerializer(serializers.Serializer):
    project_id = serializers.IntegerField(help_text="项目ID", required=False)
    template_list = serializers.ListSerializer(child=TemplateParamsSerializer(), help_text="模版列表", required=True)

    def validate_template_source(self, template_source):
        if template_source == PROJECT and "project_id" not in self.initial_data:
            raise serializers.ValidationError("获取项目流程的表单必须传入项目ID")

        return template_source


class BatchTemplateFormResponseSerializer(serializers.Serializer):
    result = serializers.BooleanField(help_text="请求是否成功")
    message = serializers.CharField(help_text="result=false返回错误的错误信息")
    data = serializers.DictField(help_text="返回表单输入输出参数")
