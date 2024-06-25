# -*- coding: utf-8 -*-
import json

from rest_framework import serializers

from gcloud.common_template.models import CommonTemplate
from gcloud.constants import DATETIME_FORMAT
from gcloud.contrib.appmaker.models import AppMaker
from gcloud.periodictask.models import PeriodicTask
from gcloud.taskflow3.models import TaskFlowInstance
from gcloud.tasktmpl3.models import TaskTemplate


class TaskTemplateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True, help_text="模板id")
    name = serializers.CharField(read_only=True, help_text="模板名称")
    creator = serializers.CharField(read_only=True, help_text="创建者名称")
    editor = serializers.CharField(read_only=True, help_text="编辑者名称")
    create_time = serializers.DateTimeField(help_text="创建时间", format=DATETIME_FORMAT, required=False)
    edit_time = serializers.DateTimeField(help_text="编辑时间", format=DATETIME_FORMAT, required=False)

    class Meta:
        model = TaskTemplate
        fields = [
            "id",
            "name",
            "executor_proxy",
            "creator",
            "create_time",
            "editor",
            "edit_time",
            "is_deleted",
            "notify_type",
            "notify_receivers",
            "time_out",
        ]


class CommonTaskTemplateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True, help_text="模板id")
    name = serializers.CharField(read_only=True, help_text="模板名称")
    creator = serializers.CharField(read_only=True, help_text="创建者名称")
    editor = serializers.CharField(read_only=True, help_text="编辑者名称")
    create_time = serializers.DateTimeField(help_text="创建时间", format=DATETIME_FORMAT, required=False)
    edit_time = serializers.DateTimeField(help_text="编辑时间", format=DATETIME_FORMAT, required=False)

    class Meta:
        model = CommonTemplate
        fields = [
            "id",
            "name",
            "creator",
            "create_time",
            "editor",
            "edit_time",
            "is_deleted",
            "notify_type",
            "notify_receivers",
            "time_out",
        ]


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
    executor_name = serializers.CharField(help_text="执行者名称", read_only=True)
    name = serializers.CharField(source="pipeline_instance.name", read_only=True)

    class Meta:
        model = TaskFlowInstance
        fields = "__all__"


class AppmakerSerializer(serializers.ModelSerializer):
    creator_name = serializers.CharField(help_text="创建者名", read_only=True)
    editor_name = serializers.CharField(help_text="编辑者名", read_only=True)
    template_name = serializers.CharField(source="task_template_name", read_only=True)
    template_id = serializers.IntegerField(source="task_template.id", read_only=True)
    edit_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S %z", read_only=True)

    class Meta:
        model = AppMaker
        fields = "__all__"


class PeriodicTaskSerializer(serializers.ModelSerializer):
    last_run_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S %z", read_only=True)
    create_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S %z", read_only=True)
    edit_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S %z", read_only=True)
    is_latest = serializers.SerializerMethodField(help_text="版本是否最新", read_only=True)
    template_scheme_ids = serializers.SerializerMethodField(
        help_text="任务创建时执行方案列表，任务创建以pipeline_tree为准，仅供参考", read_only=True
    )
    template_id = serializers.IntegerField(help_text="模板 id", read_only=True)

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
            "id",
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
            "is_latest",
            "template_scheme_ids",
            "template_version",
        ]


class UpdatePeriodicTaskSerializer(serializers.Serializer):
    task_id = serializers.IntegerField(help_text="task_id")
    project = serializers.IntegerField(help_text="项目 id")
    cron = serializers.DictField(help_text="cron 表达式")
    name = serializers.CharField(help_text="任务名")
    constants = serializers.DictField(help_text="参数")


class UpdateClockedTaskSerializer(serializers.Serializer):
    task_name = serializers.CharField(help_text="任务名")
    task_parameters = serializers.DictField(help_text="任务参数")
    editor = serializers.CharField(help_text="编辑人", required=False)
    plan_start_time = serializers.CharField(help_text="开始时间", required=False)
