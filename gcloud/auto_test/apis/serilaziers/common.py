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

from gcloud.auto_test.apis.permission import (
    AUTO_TEST_PROJECT_SCOPES,
    AUTO_TEST_SCOPE_CHOICES,
    AUTO_TEST_TOKEN_DEFAULT_EXPIRE_SECONDS,
    get_auto_test_token_max_expire_seconds,
)


class IdsListSerializer(serializers.Serializer):
    """用于一些批量操作参数序列化使用"""

    ids_list = serializers.ListField(help_text="ID列表", child=serializers.IntegerField(), allow_empty=False)
    project_id = serializers.IntegerField(help_text="项目ID", required=False, min_value=1)


class BatchDeleteSerialzer(serializers.Serializer):
    pass


class AutoTestTokenSerialzer(serializers.Serializer):
    scope = serializers.ChoiceField(help_text="资源范围", choices=AUTO_TEST_SCOPE_CHOICES)
    project_id = serializers.IntegerField(help_text="项目ID", required=False, min_value=1)
    expire = serializers.IntegerField(
        help_text="超时时间",
        required=False,
        default=AUTO_TEST_TOKEN_DEFAULT_EXPIRE_SECONDS,
        min_value=1,
    )

    def validate_expire(self, value):
        max_expire = get_auto_test_token_max_expire_seconds()
        if value > max_expire:
            raise serializers.ValidationError(f"超时时间不能超过{max_expire}秒")
        return value

    def validate(self, attrs):
        scope = attrs["scope"]
        has_project_id = bool(attrs.get("project_id"))
        if scope in AUTO_TEST_PROJECT_SCOPES and not has_project_id:
            raise serializers.ValidationError({"project_id": "当前资源范围必须传入项目ID"})

        if scope not in AUTO_TEST_PROJECT_SCOPES and has_project_id:
            raise serializers.ValidationError({"project_id": "当前资源范围不支持项目ID"})

        return attrs
