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


class IncludeProjectSerializer(serializers.Serializer):
    include_executor_proxy = serializers.BooleanField(required=False, help_text="项目代理信息")
    include_staff_groups = serializers.BooleanField(required=False, help_text="人员分组信息")


class IncludeTemplateSerializer(serializers.Serializer):
    include_executor_proxy = serializers.BooleanField(required=False, help_text="模板代理信息")
    include_subprocess = serializers.BooleanField(required=False, help_text="子流程信息")
    include_constants = serializers.BooleanField(required=False, help_text="全局变量")
    include_notify = serializers.BooleanField(required=False, help_text="通知信息")
    include_labels = serializers.BooleanField(required=False, help_text="标签信息")


class IncludeTaskSerializer(serializers.Serializer):
    include_edit_info = serializers.BooleanField(required=False, help_text="任务更新信息")
    include_webhook_history = serializers.BooleanField(required=False, help_text="webhook回调信息")
    include_children_status = serializers.BooleanField(required=False, help_text="任务节点状态")
