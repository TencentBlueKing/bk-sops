# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from gcloud.contrib.operate_record.apis.drf.serilaziers.operate_record import (
    TaskOperateRecordSetSerializer,
    TemplateOperateRecordSetSerializer,
)
from gcloud.contrib.operate_record.models import TaskOperateRecord, TemplateOperateRecord
from gcloud.core.apis.drf.exceptions import ObjectDoesNotExistException
from gcloud.core.apis.drf.permission import IamPermission, IamPermissionInfo
from gcloud.core.apis.drf.viewsets import GcloudListViewSet
from gcloud.iam_auth import IAMMeta, res_factory
from gcloud.taskflow3.models import TaskFlowInstance
from gcloud.tasktmpl3.models import TaskTemplate


class TemplateOperateRecordSetPermission(IamPermission):
    actions = {
        "list": IamPermissionInfo(IAMMeta.FLOW_VIEW_ACTION, res_factory.resources_for_flow, id_field="instance_id"),
    }


class TaskOperateRecordSetPermission(IamPermission):
    actions = {
        "list": IamPermissionInfo(IAMMeta.TASK_VIEW_ACTION, res_factory.resources_for_task, id_field="instance_id"),
    }


class TaskOperateRecordSetViewSet(GcloudListViewSet):
    queryset = TaskOperateRecord.objects.all().order_by("-operate_date")
    serializer_class = TaskOperateRecordSetSerializer
    permission_classes = [permissions.IsAuthenticated, TaskOperateRecordSetPermission]

    def get_serializer_data(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data

    def list(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=self.request.query_params)
        serializer.is_valid(raise_exception=True)
        project_id = serializer.validated_data["project_id"]
        instance_id = serializer.validated_data["instance_id"]
        node_id = serializer.validated_data.get("node_id")
        task = TaskFlowInstance.objects.filter(
            id=instance_id,
            project__tenant_id=request.user.tenant_id,
        ).first()
        if task is None:
            raise ObjectDoesNotExistException("Task id: {} does not exist".format(instance_id))
        if task.project_id != project_id:
            raise PermissionDenied("Task does not belong to the requested project")
        if node_id:
            filters = {"project_id": project_id, "instance_id": instance_id, "node_id": node_id}
        else:
            filters = {"project_id": project_id, "instance_id": instance_id}
        queryset = self.get_queryset().filter(**filters)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class TemplateOperateRecordSetViewSet(GcloudListViewSet):
    queryset = TemplateOperateRecord.objects.all().order_by("-operate_date")
    serializer_class = TemplateOperateRecordSetSerializer
    permission_classes = [permissions.IsAuthenticated, TemplateOperateRecordSetPermission]

    def get_serializer_data(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data

    def list(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=self.request.query_params)
        serializer.is_valid(raise_exception=True)
        # 获取项目id, -1 为公共流程
        project_id = serializer.validated_data.get("project_id", "-1")
        instance_id = serializer.validated_data["instance_id"]
        template = TaskTemplate.objects.filter(
            id=instance_id,
            project__tenant_id=request.user.tenant_id,
        ).first()
        if template is None:
            raise ObjectDoesNotExistException("Template id: {} does not exist".format(instance_id))
        if template.project_id != project_id:
            raise PermissionDenied("Template does not belong to the requested project")
        queryset = self.get_queryset().filter(project_id=project_id, instance_id=instance_id)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
