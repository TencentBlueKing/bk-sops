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

from rest_framework import mixins, permissions
from rest_framework.pagination import LimitOffsetPagination

from gcloud.contrib.appmaker.models import AppMaker
from gcloud.contrib.audit.utils import bk_audit_add_event
from gcloud.core.apis.drf.permission import HAS_OBJECT_PERMISSION, IamPermission, IamPermissionInfo
from gcloud.core.apis.drf.resource_helpers import ViewSetResourceHelper
from gcloud.core.apis.drf.serilaziers.appmaker import AppmakerSerializer
from gcloud.core.apis.drf.viewsets.base import GcloudReadOnlyViewSet
from gcloud.iam_auth import IAMMeta, get_iam_client, res_factory


class AppmakerPermission(IamPermission):
    actions = {
        "list": IamPermissionInfo(
            IAMMeta.PROJECT_VIEW_ACTION, res_factory.resources_for_project, id_field="project__id"
        ),
        "retrieve": IamPermissionInfo(
            IAMMeta.MINI_APP_VIEW_ACTION, res_factory.resources_for_mini_app_obj, check_hook=HAS_OBJECT_PERMISSION
        ),
        "destroy": IamPermissionInfo(
            IAMMeta.MINI_APP_DELETE_ACTION, res_factory.resources_for_mini_app_obj, HAS_OBJECT_PERMISSION
        ),
    }


class AppmakerListViewSet(GcloudReadOnlyViewSet, mixins.DestroyModelMixin):
    project_id_multi_tenant_filter = True
    queryset = AppMaker.objects.filter(is_deleted=False)
    serializer_class = AppmakerSerializer
    permission_classes = [permissions.IsAuthenticated, AppmakerPermission]
    filter_fields = {"editor": ["exact"], "project__id": ["exact"], "edit_time": ["gte", "lte"], "name": ["icontains"]}
    pagination_class = LimitOffsetPagination

    @staticmethod
    def iam_resource_helper(tenant_id):
        iam_client = get_iam_client(tenant_id=tenant_id)
        return ViewSetResourceHelper(
            iam=iam_client,
            resource_func=res_factory.resources_for_mini_app_obj,
            actions=[
                IAMMeta.MINI_APP_CREATE_TASK_ACTION,
                IAMMeta.MINI_APP_DELETE_ACTION,
                IAMMeta.MINI_APP_EDIT_ACTION,
                IAMMeta.MINI_APP_VIEW_ACTION,
            ],
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        bk_audit_add_event(
            username=request.user.username,
            action_id=IAMMeta.MINI_APP_VIEW_ACTION,
            resource_id=IAMMeta.MINI_APP_RESOURCE,
            instance=instance,
        )
        return super(AppmakerListViewSet, self).retrieve(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        bk_audit_add_event(
            username=request.user.username,
            action_id=IAMMeta.MINI_APP_DELETE_ACTION,
            resource_id=IAMMeta.MINI_APP_RESOURCE,
            instance=instance,
        )
        return super(AppmakerListViewSet, self).destroy(request, *args, **kwargs)
