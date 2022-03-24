# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2022 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
from rest_framework import serializers

from gcloud.taskflow3.models import TaskFlowInstance
from gcloud.core.apis.drf.serilaziers.project import ProjectSerializer


class TaskSerializer(serializers.ModelSerializer):

    create_time = serializers.DateTimeField(
        format="%Y-%m-%d %H:%M:%S %z", read_only=True, source="pipeline_instance.create_time"
    )
    finish_time = serializers.DateTimeField(
        format="%Y-%m-%d %H:%M:%S %z", read_only=True, source="pipeline_instance.finish_time"
    )
    start_time = serializers.DateTimeField(
        format="%Y-%m-%d %H:%M:%S %z", read_only=True, source="pipeline_instance.start_time"
    )
    is_expired = serializers.BooleanField(source="pipeline_instance.is_expired", read_only=True)
    is_finished = serializers.BooleanField(source="pipeline_instance.is_finished", read_only=True)
    is_revoked = serializers.BooleanField(source="pipeline_instance.is_revoked", read_only=True)
    is_started = serializers.BooleanField(source="pipeline_instance.is_started", read_only=True)
    name = serializers.CharField(source="pipeline_instance.name", read_only=True)
    subprocess_info = serializers.JSONField(read_only=True)
    pipeline_tree = serializers.CharField(read_only=True)
    project = ProjectSerializer()

    class Meta:
        model = TaskFlowInstance
        fields = "__all__"
