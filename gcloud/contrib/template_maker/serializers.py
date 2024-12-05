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
from gcloud.contrib.template_maker.models import TemplateSharedRecord


class TemplateSharedRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = TemplateSharedRecord
        fields = "__all__"

    def validate(self, attrs):
        project_id = attrs.get("project_id")
        template_id = attrs.get("template_id")

        if not project_id or not template_id:
            raise serializers.ValidationError("Project ID and Template ID cannot be empty.")

        if TemplateSharedRecord.objects.filter(project_id=project_id, template_id=template_id).exists():
            raise serializers.ValidationError("The template has been shared")

        return attrs
