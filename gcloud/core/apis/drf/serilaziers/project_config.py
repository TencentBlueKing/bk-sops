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

from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from gcloud.core.models import ProjectConfig


class ProjectConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectConfig
        fields = ["project_id", "executor_proxy", "executor_proxy_exempts"]
        read_only_fields = ["project_id"]

    def validate_executor_proxy(self, value):
        user = getattr(self.context.get("request"), "user", None)
        if not user:
            raise serializers.ValidationError("user can not be empty.")
        if user.username != value and value:
            raise serializers.ValidationError(_("代理人仅可设置为本人"))
        return value
