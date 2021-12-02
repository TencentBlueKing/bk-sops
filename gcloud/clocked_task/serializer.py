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
import json
from typing import Any, Dict

from rest_framework import serializers

from gcloud.clocked_task.models import ClockedTask
from gcloud.utils.drf.serializer import ReadWriteSerializerMethodField


class ClockedTaskSerializer(serializers.ModelSerializer):
    task_parameters = ReadWriteSerializerMethodField(help_text="任务创建相关数据")
    creator = serializers.CharField(help_text="计划任务创建人", read_only=True)
    plan_start_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    notify_type = ReadWriteSerializerMethodField(help_text="计划任务事件通知方式", required=False)
    notify_receivers = ReadWriteSerializerMethodField(help_text="计划任务事件通知人", required=False)

    def get_task_parameters(self, obj) -> Dict[str, Any]:
        if not getattr(obj, "task_params") or not obj.task_params:
            return dict()
        return json.loads(obj.task_params)

    def set_task_parameters(self, data):
        return {"task_params": json.dumps(data)}

    def get_notify_type(self, obj) -> Dict[str, Any]:
        if not getattr(obj, "notify_type") or not obj.notify_type:
            return dict()
        return json.loads(obj.notify_type)

    def set_notify_type(self, data):
        return {"notify_type": json.dumps(data)}

    def get_notify_receivers(self, obj) -> Dict[str, Any]:
        if not getattr(obj, "notify_receivers") or not obj.notify_receivers:
            return dict()
        return json.loads(obj.notify_receivers)

    def set_notify_receivers(self, data):
        return {"notify_receivers": json.dumps(data)}

    class Meta:
        model = ClockedTask
        exclude = ("task_params",)
