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

import json

from django.utils import timezone
from rest_framework import serializers

from gcloud.core.models import Project
from gcloud.tasktmpl3.models import TaskTemplate
from gcloud.common_template.models import CommonTemplate
from gcloud.contrib.appmaker.models import AppMaker
from gcloud.taskflow3.models import TaskFlowInstance
from gcloud.constants import TASK_CREATE_METHOD, TASK_FLOW_TYPE, TEMPLATE_SOURCE, DATETIME_FORMAT
from gcloud.core.apis.drf.serilaziers.taskflow import TaskSerializer
from pipeline_web.parser.validator import validate_web_pipeline_tree
from pipeline.exceptions import PipelineException


class TaskFlowInstanceSerializer(TaskSerializer):
    id = serializers.IntegerField(help_text="任务ID")
    instance_id = serializers.IntegerField(help_text="任务实例ID")
    category_name = serializers.CharField(help_text="分类名称")
    creator_name = serializers.CharField(help_text="创建者名称")
    executor_name = serializers.CharField(help_text="执行者名称")
    elapsed_time = serializers.IntegerField(help_text="执行耗时")

    class Meta:
        model = TaskFlowInstance
        fields = "__all__"


class RetrieveTaskFlowInstanceSerializer(TaskFlowInstanceSerializer):
    pipeline_tree = serializers.SerializerMethodField()
    primitive_template_id = serializers.SerializerMethodField()
    primitive_template_source = serializers.SerializerMethodField()

    def get_pipeline_tree(self, obj):
        return json.dumps(obj.pipeline_tree)

    def get_primitive_template_id(self, obj):
        primitive_template_id = obj.template_id
        if getattr(obj, "is_child_taskflow", False) and getattr(obj, "extra_info", None):
            extra_info = json.loads(obj.extra_info)
            primitive_template_id = extra_info.get("primitive_template_id")
            if primitive_template_id:
                return str(primitive_template_id)
        return primitive_template_id

    def get_primitive_template_source(self, obj):
        primitive_template_source = obj.template_source
        if getattr(obj, "is_child_taskflow", False) and getattr(obj, "extra_info", None):
            extra_info = json.loads(obj.extra_info)
            primitive_template_source = extra_info.get("primitive_template_source")
            if primitive_template_source:
                return primitive_template_source
        return primitive_template_source


class CreateTaskFlowInstanceSerializer(TaskSerializer):
    id = serializers.IntegerField(help_text="任务ID", read_only=True)
    instance_id = serializers.IntegerField(help_text="任务实例ID", read_only=True)
    name = serializers.CharField(help_text="任务名称")
    description = serializers.CharField(help_text="任务描述", allow_blank=True, write_only=True)
    project = serializers.IntegerField(help_text="项目ID", write_only=True)
    template = serializers.IntegerField(help_text="模板ID", write_only=True)
    creator = serializers.CharField(help_text="创建人")
    pipeline_tree = serializers.CharField(help_text="pipeline流程树")
    create_method = serializers.ChoiceField(choices=TASK_CREATE_METHOD, help_text="创建方式")
    create_info = serializers.IntegerField(help_text="创建信息,使用轻应用创建任务时传入轻应用ID", default=-1)
    flow_type = serializers.ChoiceField(choices=TASK_FLOW_TYPE, help_text="任务类型")
    template_source = serializers.ChoiceField(choices=TEMPLATE_SOURCE, help_text="模板来源")

    def validate_project(self, value):
        try:
            project = Project.objects.get(id=int(value))
        except Project.DoesNotExist:
            raise serializers.ValidationError(f"id={value}的项目不存在")
        return project

    def validate_template(self, value):
        template_source = self.initial_data["template_source"]
        model_cls = TaskTemplate if template_source == "project" else CommonTemplate
        try:
            template = model_cls.objects.get(id=value)
        except model_cls.DoesNotExist:
            raise serializers.ValidationError(f"id={value}的模板不存在")
        return template

    def validate_create_method(self, value):
        if value == "app_maker":
            app_maker_id = self.initial_data["create_info"]
            try:
                AppMaker.objects.get(id=app_maker_id)
            except AppMaker.DoesNotExist:
                raise serializers.ValidationError(f"id={app_maker_id}的轻应用不存在")
        return value

    def validate_pipeline_tree(self, value):
        try:
            value = json.loads(value)
            validate_web_pipeline_tree(value)
        except PipelineException as e:
            raise serializers.ValidationError(str(e))
        return value

    class Meta:
        model = TaskFlowInstance
        exclude = ["current_flow"]


class ListChildrenTaskFlowQuerySerializer(serializers.Serializer):
    root_task_id = serializers.IntegerField(help_text="根任务ID")
    project_id = serializers.IntegerField(help_text="项目ID, 用于鉴权")


class ListChildrenTaskFlowResponseSerializer(serializers.Serializer):
    tasks = serializers.ListSerializer(child=TaskFlowInstanceSerializer())
    relations = serializers.DictField(help_text="任务关系, key为父任务ID, value为子任务ID列表")


class RootTaskflowQuerySerializer(serializers.Serializer):
    task_ids = serializers.CharField(help_text="任务ID列表, 多个任务ID之间用逗号分隔")
    project_id = serializers.IntegerField(help_text="项目ID, 用于鉴权")


class NodeSnapshotQuerySerializer(serializers.Serializer):
    node_id = serializers.CharField(help_text="节点ID", required=True)
    subprocess_stack = serializers.CharField(help_text="子流程节点堆栈信息", required=True)

    def to_representation(self, instance):
        data = super(NodeSnapshotQuerySerializer, self).to_representation(instance)
        data["subprocess_stack"] = json.loads(data.get("subprocess_stack", "[]"))
        return data


class NodeSnapshotResponseSerializer(serializers.Serializer):
    component = serializers.DictField(help_text="组件快照信息")


class RootTaskflowResponseSerializer(serializers.Serializer):
    has_children_taskflow = serializers.DictField(help_text="是否有子任务流, key为任务ID, value为是否有子任务")


class NodeExecutionRecordQuerySerializer(serializers.Serializer):
    template_node_id = serializers.CharField(help_text="查询节点对应的流程节点 ID")


class NodeExecutionTimeSerializer(serializers.Serializer):
    archived_time = serializers.DateTimeField(
        help_text="归档时间", default_timezone=timezone.get_current_timezone(), format=DATETIME_FORMAT
    )
    elapsed_time = serializers.IntegerField(help_text="执行耗时")


class NodeExecutionRecordResponseSerializer(serializers.Serializer):
    execution_time = serializers.ListField(child=NodeExecutionTimeSerializer(help_text="执行时间"))
    total = serializers.IntegerField(help_text="执行总数")
