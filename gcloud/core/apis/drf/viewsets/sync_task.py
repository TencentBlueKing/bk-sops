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
from rest_framework import permissions
from rest_framework.exceptions import NotAcceptable

from gcloud.iam_auth import IAMMeta
from gcloud.external_plugins.models import CachePackageSource, SyncTask, RUNNING

from .base import GcloudModelViewSet
from ..filter import VarietyFilterSet, ALL
from ..serilaziers import SyncTaskSerializer
from ..permission import IamPermissionInfo, IamPermission
from ..viewsets.package_source import get_all_source_objects


class SyncTaskPermission(IamPermission):
    actions = {
        "list": IamPermissionInfo(IAMMeta.ADMIN_VIEW_ACTION, res=[], has_object_permission=False),
        "retrieve": IamPermissionInfo(IAMMeta.ADMIN_VIEW_ACTION, res=[], has_permission=False),
        "partial_update": IamPermissionInfo(IAMMeta.ADMIN_EDIT_ACTION, obj_res=[], has_permission=False),
        "update": IamPermissionInfo(IAMMeta.ADMIN_EDIT_ACTION, obj_res=[], has_permission=False),
        "create": IamPermissionInfo(IAMMeta.ADMIN_EDIT_ACTION, res=[], has_object_permission=False),
        "destroy": IamPermissionInfo(pass_all=True),
    }


class SyncTaskFilter(VarietyFilterSet):
    class Meta:
        model = SyncTask
        q_fields = ["id", "pipeline_template__name"]
        fields = {
            "id": ["exact"],
            "creator": ALL,
            "create_method": ["exact"],
            "start_time": ["range", "in", "exact"],
            "finish_time": ["range", "in", "exact"],
            "status": ALL,
        }


class SyncTaskViewSet(GcloudModelViewSet):
    queryset = SyncTask.objects.all()

    serializer_class = SyncTaskSerializer
    permission_classes = [permissions.IsAuthenticated, SyncTaskPermission]
    filterset_class = SyncTaskFilter

    def create(self, request, *args, **kwargs):
        if SyncTask.objects.filter(status=RUNNING).exists():
            raise NotAcceptable("There is already a running sync task, please wait for it to complete and try again")
        if not CachePackageSource.objects.all().exists():
            raise NotAcceptable("No cache package found, please add cache package in Backend Manage")
        if len(get_all_source_objects()) <= 1:
            raise NotAcceptable("No original packages found, please add original packages in Backend Manage")
        return super(SyncTaskViewSet, self).create(request, *args, **kwargs)
