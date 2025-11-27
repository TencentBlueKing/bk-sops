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
from webhook.config import webhook_settings
from webhook.models import Event


class IncludeProjectSerializer(serializers.Serializer):
    include_executor_proxy = serializers.BooleanField(required=False, help_text="项目代理信息", default=False)
    include_staff_groups = serializers.BooleanField(required=False, help_text="人员分组信息", default=False)


class IncludeTemplateSerializer(serializers.Serializer):
    include_executor_proxy = serializers.BooleanField(required=False, help_text="模板代理信息", default=False)
    include_subprocess = serializers.BooleanField(required=False, help_text="子流程信息", default=False)
    include_constants = serializers.BooleanField(required=False, help_text="全局变量", default=False)
    include_notify = serializers.BooleanField(required=False, help_text="通知信息", default=False)
    include_labels = serializers.BooleanField(required=False, help_text="标签信息", default=False)


class IncludeTaskSerializer(serializers.Serializer):
    include_edit_info = serializers.BooleanField(required=False, help_text="任务更新信息", default=False)
    include_webhook_history = serializers.BooleanField(required=False, help_text="webhook回调信息", default=False)
    include_children_status = serializers.BooleanField(required=False, help_text="任务节点状态", default=False)


class WebhookSerializer(serializers.Serializer):
    endpoint = serializers.URLField(help_text="webhook endpoint", max_length=255, required=True)
    method = serializers.CharField(help_text="webhook method", max_length=255, required=False)
    extra_info = serializers.JSONField(help_text="额外扩展信息", required=False)
    events = serializers.ListField(child=serializers.CharField(), help_text="webhook事件列表", required=True)
    template_ids = serializers.ListField(child=serializers.IntegerField(), help_text="模板ID列表", required=True)

    def validate_events(self, events: list):
        not_support_events = set(events) - set(Event.objects.all_events() + [webhook_settings.ALL_EVENTS_KEY])
        if not_support_events:
            raise serializers.ValidationError(f"校验失败，events中包含不支持的事件类型, 不支持事件类型: {not_support_events}")
        return events
