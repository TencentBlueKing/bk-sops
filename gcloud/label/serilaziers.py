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

from gcloud.label.models import Label


class NewLabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Label
        fields = "__all__"

    def validate_is_default(self, value):
        if value is True:
            raise serializers.ValidationError("is_default should be False")
        return value

    def validate(self, attrs):
        if attrs.get("project_id") and attrs.get("from_space_id"):
            raise serializers.ValidationError("project_id and from_space_id can not both be filled")
        return attrs
