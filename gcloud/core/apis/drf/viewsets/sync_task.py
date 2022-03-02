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

from gcloud.core.apis.drf.viewsets.base import GcloudModelViewSet
from gcloud.core.apis.drf.filtersets import ALL_LOOKUP, AllLookupSupportFilterSet
from gcloud.core.apis.drf.serilaziers import SyncTaskSerializer
from gcloud.core.apis.drf.permission import IamPermissionInfo, IamPermission, HAS_OBJECT_PERMISSION
from gcloud.core.apis.drf.viewsets.package_source import get_all_source_objects


class SyncTaskPermission(IamPermission):
    actions = {
        "list": IamPermissionInfo(IAMMeta.ADMIN_VIEW_ACTION),
        "retrieve": IamPermissionInfo(IAMMeta.ADMIN_VIEW_ACTION, check_hook=HAS_OBJECT_PERMISSION),
        "partial_update": IamPermissionInfo(IAMMeta.ADMIN_EDIT_ACTION, check_hook=HAS_OBJECT_PERMISSION),
        "update": IamPermissionInfo(IAMMeta.ADMIN_EDIT_ACTION, check_hook=HAS_OBJECT_PERMISSION),
        "create": IamPermissionInfo(IAMMeta.ADMIN_EDIT_ACTION),
        "destroy": IamPermissionInfo(pass_all=True),
    }


class SyncTaskFilter(AllLookupSupportFilterSet):
    class Meta:
        model = SyncTask
        fields = {
            "id": ["exact"],
            "creator": ALL_LOOKUP,
            "create_method": ["exact"],
            "start_time": ["range", "in", "exact"],
            "finish_time": ["range", "in", "exact"],
            "status": ALL_LOOKUP,
        }


class SyncTaskViewSet(GcloudModelViewSet):
    queryset = SyncTask.objects.all()
    serializer_class = SyncTaskSerializer
    permission_classes = [permissions.IsAuthenticated, SyncTaskPermission]
    search_fields = ["id", "pipeline_template__name"]
    filterset_class = SyncTaskFilter

    def create(self, request, *args, **kwargs):
        if SyncTask.objects.filter(status=RUNNING).exists():
            raise NotAcceptable("There is already a running sync task, please wait for it to complete and try again")
        if not CachePackageSource.objects.all().exists():
            raise NotAcceptable("No cache package found, please add cache package in Backend Manage")
        if len(get_all_source_objects()) <= 1:
            raise NotAcceptable("No original packages found, please add original packages in Backend Manage")
        return super(SyncTaskViewSet, self).create(request, *args, **kwargs)
