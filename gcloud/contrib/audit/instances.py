# -*- coding: utf-8 -*-
import copy

from bk_audit.log.models import AuditInstance
from django.forms import model_to_dict

from gcloud.clocked_task.serializer import ClockedTaskSerializer
from gcloud.contrib.audit.serializers import (
    AppmakerSerializer,
    CommonTaskTemplateSerializer,
    PeriodicTaskSerializer,
    TaskSerializer,
    TaskTemplateSerializer,
    UpdateClockedTaskSerializer,
    UpdatePeriodicTaskSerializer,
)
from gcloud.core.apis.drf.serilaziers import CreateTaskTemplateSerializer, ProjectSerializer
from gcloud.core.apis.drf.serilaziers.common_template import CreateCommonTemplateSerializer


class BaseInstance:
    def __init__(self, inst, origin_data: dict = None):
        self.inst = inst
        self.origin_data = copy.deepcopy(origin_data)

    def prepare_origin_data(self):
        return self.origin_data

    @property
    def instance_id(self):
        return self.inst.id

    @property
    def instance_name(self):
        return self.inst.name

    @property
    def instance_sensitivity(self):
        return 0

    @property
    def instance_origin_data(self):
        return self.prepare_origin_data()

    @property
    def instance_data(self):
        return model_to_dict(self.inst)

    @property
    def instance(self):
        return AuditInstance(self)


class TaskTemplateInstance(BaseInstance):
    def prepare_origin_data(self):
        if not self.origin_data:
            return {}
        ser = CreateTaskTemplateSerializer(data=self.origin_data)
        ser.is_valid(raise_exception=True)
        ser.validated_data.pop("pipeline_tree", None)
        ser.validated_data.pop("project", None)
        return dict(ser.validated_data)

    @property
    def instance_name(self):
        return self.inst.pipeline_template.name

    @property
    def instance_data(self):
        return TaskTemplateSerializer(self.inst).data


class CommonTaskTemplateInstance(BaseInstance):
    def prepare_origin_data(self):
        if not self.origin_data:
            return {}
        ser = CreateCommonTemplateSerializer(data=self.origin_data)
        ser.is_valid(raise_exception=True)
        ser.validated_data.pop("pipeline_tree", None)
        ser.validated_data.pop("project", None)
        return dict(ser.validated_data)

    @property
    def instance_name(self):
        return self.inst.pipeline_template.name

    @property
    def instance_data(self):
        return CommonTaskTemplateSerializer(self.inst).data


class ProjectInstance(BaseInstance):
    def prepare_origin_data(self):
        if not self.origin_data:
            return {}
        ser = ProjectSerializer(data=self.origin_data)
        ser.is_valid(raise_exception=True)
        return dict(ser.validated_data)

    @property
    def instance_data(self):
        return ProjectSerializer(self.inst).data


class TaskInstance(BaseInstance):
    def prepare_origin_data(self):
        if not self.origin_data:
            return {}
        ser = TaskSerializer(data=self.origin_data)
        ser.is_valid(raise_exception=True)
        return dict(ser.validated_data)

    @property
    def instance_data(self):
        return TaskSerializer(self.inst).data


class MiniAppInstance(BaseInstance):
    @property
    def instance_data(self):
        return AppmakerSerializer(self.inst).data


class PeriodicTaskInstance(BaseInstance):
    def prepare_origin_data(self):
        if not self.origin_data:
            return {}
        self.origin_data["task_id"] = self.origin_data["taskId"]
        ser = UpdatePeriodicTaskSerializer(data=self.origin_data)
        ser.is_valid(raise_exception=True)
        return dict(ser.validated_data)

    @property
    def instance_data(self):
        return PeriodicTaskSerializer(self.inst).data


class ClockedTaskInstance(BaseInstance):
    def prepare_origin_data(self):
        if not self.origin_data:
            return {}
        ser = UpdateClockedTaskSerializer(data=self.origin_data)
        ser.is_valid(raise_exception=True)
        return dict(ser.validated_data)

    @property
    def instance_data(self):
        return ClockedTaskSerializer(self.inst).data

    @property
    def instance_name(self):
        return self.inst.task_name


INSTANCE_MAP = {
    "flow": TaskTemplateInstance,
    "common_flow": CommonTaskTemplateInstance,
    "project": ProjectInstance,
    "task": TaskInstance,
    "mini_app": MiniAppInstance,
    "periodic_task": PeriodicTaskInstance,
    "clocked_task": ClockedTaskInstance,
}


def build_instance(instance_type, instance, origin_data=None):
    instance_cls = INSTANCE_MAP.get(instance_type, None)
    if not instance_cls:
        return None
    if not instance:
        return None
    instance = instance_cls(instance, origin_data).instance
    return instance
