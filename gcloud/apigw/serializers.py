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


class IncludeOptionsSerializer(serializers.Serializer):
    include_subprocess = serializers.IntegerField(required=False, default=0)
    include_constants = serializers.IntegerField(required=False, default=0)
    include_executor_proxy = serializers.IntegerField(required=False, default=0)
    include_notify = serializers.IntegerField(required=False, default=0)
    include_edit_info = serializers.IntegerField(required=False, default=0)
    include_webhook_history = serializers.IntegerField(required=False, default=0)
    include_staff_groups = serializers.IntegerField(required=False, default=0)
    include_children_status = serializers.IntegerField(required=False, default=0)
    include_labels = serializers.IntegerField(required=False, default=0)

    def validate(self, attrs):
        for key, value in attrs.items():
            if value != 1:
                attrs[key] = 0
        return attrs
