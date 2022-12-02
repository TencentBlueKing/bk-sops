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
from rest_framework.fields import SerializerMethodField

import env
import ujson as json
from rest_framework import serializers
from rest_framework.validators import ValidationError
from django_celery_beat.models import PeriodicTask as CeleryTask, CrontabSchedule as DjangoCeleryBeatCrontabSchedule
from django.utils.translation import ugettext_lazy as _

from gcloud.core.models import Project
from gcloud.constants import PROJECT
from gcloud.core.models import ProjectConfig
from pipeline.contrib.periodic_task.models import PeriodicTask as PipelinePeriodicTask
from gcloud.core.apis.drf.serilaziers.project import ProjectSerializer
from gcloud.periodictask.models import PeriodicTask
from gcloud.utils.drf.serializer import ReadWriteSerializerMethodField
import logging

logger = logging.getLogger("root")


class CeleryTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = CeleryTask
        fields = "__all__"


class PipelinePeriodicTaskSerializer(serializers.ModelSerializer):
    celery_task = CeleryTaskSerializer()
    extra_info = SerializerMethodField()

    def get_extra_info(self, obj):
        return obj.extra_info

    class Meta:
        model = PipelinePeriodicTask
        fields = [
            "celery_task",
            "name",
            "creator",
            "cron",
            "extra_info",
            "id",
            "last_run_at",
            "priority",
            "queue",
            "total_run_count",
        ]


class PeriodicTaskReadOnlySerializer(serializers.ModelSerializer):

    task = PipelinePeriodicTaskSerializer()
    project = ProjectSerializer()
    last_run_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S %z", read_only=True)
    create_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S %z", read_only=True)
    edit_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S %z", read_only=True)
    is_latest = serializers.SerializerMethodField(help_text="版本是否最新", read_only=True)
    template_scheme_ids = serializers.SerializerMethodField(
        help_text="任务创建时执行方案列表，任务创建以pipeline_tree为准，仅供参考", read_only=True
    )

    def get_is_latest(self, obj):
        return obj.template_version == obj.template.version if obj.template_version else None

    def get_template_scheme_ids(self, obj):
        try:
            return json.loads(obj.template_scheme_ids)
        except Exception:
            return obj.template_scheme_ids

    class Meta:
        model = PeriodicTask
        fields = [
            "project",
            "id",
            "task",
            "creator",
            "editor",
            "create_time",
            "edit_time",
            "cron",
            "enabled",
            "last_run_at",
            "name",
            "task_template_name",
            "template_id",
            "template_source",
            "total_run_count",
            "form",
            "pipeline_tree",
            "is_latest",
            "template_scheme_ids",
            "template_version",
        ]


def check_cron_params(cron, project):
    # DB cron 属性最大允许字符长度数量
    max_length = 128
    project_id = project.id if isinstance(project, Project) else project
    # 计算周期任务拼接字符串长度
    schedule_length = len(
        str(
            DjangoCeleryBeatCrontabSchedule(
                minute=cron.get("minute", "*"),
                hour=cron.get("hour", "*"),
                day_of_week=cron.get("day_of_week", "*"),
                day_of_month=cron.get("day_of_month", "*"),
                month_of_year=cron.get("month_of_year", "*"),
                timezone=Project.objects.filter(id=project_id).first().time_zone,
            )
        )
    )
    if schedule_length > max_length:
        raise ValidationError("周期任务时间格式过长")


class CreatePeriodicTaskSerializer(serializers.ModelSerializer):
    project = serializers.IntegerField(write_only=True)
    cron = serializers.DictField(write_only=True)
    template_source = serializers.CharField(required=False, default=PROJECT)
    pipeline_tree = ReadWriteSerializerMethodField()
    template_scheme_ids = ReadWriteSerializerMethodField()
    name = serializers.CharField()
    template_id = serializers.IntegerField()

    def set_pipeline_tree(self, data):
        return {"pipeline_tree": json.loads(data)}

    def get_pipeline_tree(self, obj):
        return json.dumps(obj.pipeline_tree)

    def get_template_scheme_ids(self, obj):
        try:
            return json.loads(obj.template_scheme_ids)
        except Exception:
            return obj.template_scheme_ids

    def set_template_scheme_ids(self, data):
        return {"template_scheme_ids": json.dumps(data)}

    def validate_project(self, value):
        try:
            project = Project.objects.get(id=value)
            periodic_task_limit = env.PERIODIC_TASK_PROJECT_MAX_NUMBER
            project_config = ProjectConfig.objects.filter(project_id=project.id).only("max_periodic_task_num").first()
            if project_config and project_config.max_periodic_task_num > 0:
                periodic_task_limit = project_config.max_periodic_task_num
            if PeriodicTask.objects.filter(project__id=project.id).count() >= periodic_task_limit:
                message = _(f"周期任务创建失败: 项目内的周期任务数不可超过: {periodic_task_limit} | validate_project")
                logger.error(message)
                raise serializers.ValidationError(message)
            return project
        except Project.DoesNotExist:
            raise serializers.ValidationError(_("project不存在"))

    def validate(self, attrs):
        check_cron_params(attrs.get("cron"), attrs.get("project"))
        return attrs

    class Meta:
        model = PeriodicTask
        fields = ["project", "cron", "name", "template_id", "pipeline_tree", "template_source", "template_scheme_ids"]


class PatchUpdatePeriodicTaskSerializer(serializers.Serializer):
    cron = serializers.DictField(help_text="周期", required=False)
    project = serializers.IntegerField(help_text="项目ID", required=False)
    constants = serializers.DictField(help_text="执行参数", required=False)
    name = serializers.CharField(help_text="任务名", required=False)

    def validate(self, attrs):
        check_cron_params(attrs.get("cron"), attrs.get("project"))
        return attrs
