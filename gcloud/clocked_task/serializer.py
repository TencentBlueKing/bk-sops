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
import json
from datetime import datetime
from typing import Any, Dict

import pytz
from django.utils import timezone
from pipeline.exceptions import PipelineException
from rest_framework import serializers

from gcloud.clocked_task.models import ClockedTask
from gcloud.utils.drf.serializer import ReadWriteSerializerMethodField
from gcloud.utils.pipeline import validate_pipeline_tree_constants


class ClockedTaskSerializer(serializers.ModelSerializer):
    task_parameters = ReadWriteSerializerMethodField(help_text="任务创建相关数据")
    creator = serializers.CharField(help_text="计划任务创建人", read_only=True)
    editor = serializers.CharField(help_text="计划任务编辑人", read_only=True)
    state = serializers.CharField(help_text="计划任务状态", read_only=True)
    plan_start_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S%z")
    create_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S%z", read_only=True)
    edit_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S%z", read_only=True)

    def get_task_parameters(self, obj) -> Dict[str, Any]:
        if not getattr(obj, "task_params") or not obj.task_params:
            return dict()
        return json.loads(obj.task_params)

    def set_task_parameters(self, data):
        return {"task_params": json.dumps(data)}

    def validate_task_parameters(self, data):
        task_parameters = json.loads(data["task_params"])
        node_appoint_method_num = sum(
            [
                1
                for method in ["exclude_task_nodes_id", "template_schemes_id", "appoint_task_nodes_id"]
                if task_parameters.get(method)
            ]
        )
        if node_appoint_method_num > 1:
            raise serializers.ValidationError("can not use multiple method to appoint execute nodes")
        try:
            validate_pipeline_tree_constants(task_parameters.get("constants", {}))
        except PipelineException as e:
            raise serializers.ValidationError(e)
        return data

    def validate_plan_start_time(self, plan_start_time):
        now = datetime.now(tz=pytz.timezone(timezone.get_current_timezone_name()))
        if now > plan_start_time:
            raise serializers.ValidationError("Plan start time should be later than the time to create the plan")
        return plan_start_time

    class Meta:
        model = ClockedTask
        exclude = ("task_params", "notify_type", "notify_receivers")


class ClockedTaskPatchSerializer(ClockedTaskSerializer):
    editor = serializers.CharField(help_text="计划任务编辑人")
