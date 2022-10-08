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
from pipeline.models import PipelineInstance
from rest_framework import serializers
from rest_framework.fields import empty

from gcloud.contrib.function.models import FunctionTask
from gcloud.taskflow3.models import TaskFlowInstance


class FunctionTaskSerializer(serializers.ModelSerializer):

    status_name = serializers.CharField(read_only=True)
    create_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S%z", read_only=True)
    claim_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S%z", read_only=True)

    def __init__(self, instance=None, data=empty, **kwargs):
        super(FunctionTaskSerializer, self).__init__(instance, data, **kwargs)
        self.task_pipeline_instance_map = {}
        self.get_pipeline_instance_list(instance)

    def get_pipeline_instance_list(self, instance):
        if not isinstance(instance, list):
            instance = [instance]
        instance_task_id_list = [inst.task_id for inst in instance]

        # 根据所有的task_id 批量获取到所有的pipeline_instance_id
        tasks = TaskFlowInstance.objects.filter(id__in=instance_task_id_list).only("id", "pipeline_instance_id")

        pipeline_instance_id_task_map = {}
        for task in tasks:
            pipeline_instance_id_task_map[task.pipeline_instance_id] = task.id

        # 第二步，根据task_id 查询到所有的
        pipeline_instance_list = PipelineInstance.objects.filter(id__in=pipeline_instance_id_task_map.keys()).only(
            "id", "name"
        )

        for pipeline_instance in pipeline_instance_list:
            task_id = pipeline_instance_id_task_map.get(pipeline_instance.id)
            if task_id:
                self.task_pipeline_instance_map[task_id] = pipeline_instance

    def to_representation(self, instance):
        data = super(FunctionTaskSerializer, self).to_representation(instance)
        data["task"] = {"id": instance.task_id, "name": self.task_pipeline_instance_map[instance.task_id].name}
        return data

    class Meta:
        model = FunctionTask
        fields = "__all__"
