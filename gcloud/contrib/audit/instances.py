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


class AuditSnapshot(dict):
    """Marker for already serialized and sanitized origin data."""


class BaseInstance:
    def __init__(self, inst, origin_data: dict = None, data: dict = None):
        self.inst = inst
        self.origin_data = copy.deepcopy(origin_data)
        self.data = copy.deepcopy(data)

    def prepared_snapshot_origin_data(self):
        if isinstance(self.origin_data, AuditSnapshot):
            return dict(self.origin_data)
        return None

    def prepare_origin_data(self):
        snapshot = self.prepared_snapshot_origin_data()
        if snapshot is not None:
            return snapshot
        return self.origin_data

    @property
    def instance_id(self):
        if self.inst.id is None and isinstance(self.data, dict):
            return self.data.get("id")
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
        if self.data is not None:
            return self.data
        return model_to_dict(self.inst)

    @property
    def instance(self):
        return AuditInstance(self)


class TaskTemplateInstance(BaseInstance):
    def prepare_origin_data(self):
        snapshot = self.prepared_snapshot_origin_data()
        if snapshot is not None:
            return snapshot
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
        if self.data is not None:
            return self.data
        return TaskTemplateSerializer(self.inst).data


class CommonTaskTemplateInstance(BaseInstance):
    def prepare_origin_data(self):
        snapshot = self.prepared_snapshot_origin_data()
        if snapshot is not None:
            return snapshot
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
        if self.data is not None:
            return self.data
        return CommonTaskTemplateSerializer(self.inst).data


class ProjectInstance(BaseInstance):
    def prepare_origin_data(self):
        snapshot = self.prepared_snapshot_origin_data()
        if snapshot is not None:
            return snapshot
        if not self.origin_data:
            return {}
        ser = ProjectSerializer(data=self.origin_data)
        ser.is_valid(raise_exception=True)
        return dict(ser.validated_data)

    @property
    def instance_data(self):
        if self.data is not None:
            return self.data
        return ProjectSerializer(self.inst).data


class TaskInstance(BaseInstance):
    def prepare_origin_data(self):
        snapshot = self.prepared_snapshot_origin_data()
        if snapshot is not None:
            return snapshot
        if not self.origin_data:
            return {}
        ser = TaskSerializer(data=self.origin_data)
        ser.is_valid(raise_exception=True)
        return dict(ser.validated_data)

    @property
    def instance_data(self):
        if self.data is not None:
            return self.data
        return TaskSerializer(self.inst).data


class MiniAppInstance(BaseInstance):
    @property
    def instance_data(self):
        if self.data is not None:
            return self.data
        return AppmakerSerializer(self.inst).data


class PeriodicTaskInstance(BaseInstance):
    def prepare_origin_data(self):
        snapshot = self.prepared_snapshot_origin_data()
        if snapshot is not None:
            return snapshot
        if not self.origin_data:
            return {}
        self.origin_data["task_id"] = self.origin_data["taskId"]
        ser = UpdatePeriodicTaskSerializer(data=self.origin_data)
        ser.is_valid(raise_exception=True)
        return dict(ser.validated_data)

    @property
    def instance_data(self):
        if self.data is not None:
            return self.data
        return PeriodicTaskSerializer(self.inst).data


class ClockedTaskInstance(BaseInstance):
    def prepare_origin_data(self):
        snapshot = self.prepared_snapshot_origin_data()
        if snapshot is not None:
            return snapshot
        if not self.origin_data:
            return {}
        ser = UpdateClockedTaskSerializer(data=self.origin_data)
        ser.is_valid(raise_exception=True)
        return dict(ser.validated_data)

    @property
    def instance_data(self):
        if self.data is not None:
            return self.data
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


def build_instance_data(instance_type, instance, data=None):
    instance_cls = INSTANCE_MAP.get(instance_type, None)
    if not instance_cls:
        return None
    if not instance:
        return None
    return instance_cls(instance, data=data).instance_data


def build_instance(instance_type, instance, origin_data=None, data=None):
    instance_cls = INSTANCE_MAP.get(instance_type, None)
    if not instance_cls:
        return None
    if not instance:
        return None
    instance = instance_cls(instance, origin_data, data).instance
    return instance
