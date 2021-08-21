# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import re
from rest_framework import serializers

from gcloud.core.models import Project
from gcloud.project_constants.models import ProjectConstant


VALID_KEY_PATTERN = r"^[a-zA-Z_][a-zA-Z0-9_]*$"
VALID_KEY_REGEX = re.compile(VALID_KEY_PATTERN)


class ProjectConstantsSerializer(serializers.ModelSerializer):
    create_by = serializers.CharField(read_only=True)
    create_at = serializers.DateTimeField(read_only=True)
    update_by = serializers.CharField(read_only=True)
    update_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = ProjectConstant
        partial = True
        fields = [
            "id",
            "project_id",
            "name",
            "key",
            "value",
            "desc",
            "create_by",
            "create_at",
            "update_by",
            "update_at",
        ]

    def validate_project_id(self, value):
        if not Project.objects.filter(id=value).exists():
            raise serializers.ValidationError("Project with id %s not exist." % value)
        return value

    def validate_key(self, value):
        if not VALID_KEY_REGEX.match(value):
            raise serializers.ValidationError("%s not match match pattern: %s." % (value, VALID_KEY_PATTERN))
        return value

    def create(self, validated_data):
        validated_data["create_by"] = self.context["request"].user.username
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data.pop("project_id")
        validated_data["update_by"] = self.context["request"].user.username
        return super().update(instance, validated_data)
