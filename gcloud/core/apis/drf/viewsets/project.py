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

from gcloud.iam_auth import IAMMeta, res_factory
from gcloud.core.models import Project

from gcloud.core.apis.drf.filtersets import ALL_LOOKUP, AllLookupSupportFilterSet
from gcloud.core.apis.drf.serilaziers import ProjectSerializer
from gcloud.core.apis.drf.resource_helpers import ViewSetResourceHelper
from gcloud.core.apis.drf.permission import IamPermissionInfo, IamPermission, HAS_OBJECT_PERMISSION

from gcloud.core.apis.drf.viewsets.base import GcloudListViewSet, GcloudUpdateViewSet


class ProjectPermission(IamPermission):
    resource_func = res_factory.resources_for_project_obj
    actions = {
        "list": IamPermissionInfo(pass_all=True),
        "detail": IamPermissionInfo(IAMMeta.PROJECT_VIEW_ACTION, resource_func, check_hook=HAS_OBJECT_PERMISSION),
        "update": IamPermissionInfo(IAMMeta.PROJECT_EDIT_ACTION, resource_func, check_hook=HAS_OBJECT_PERMISSION),
        "retrieve": IamPermissionInfo(IAMMeta.PROJECT_VIEW_ACTION, resource_func, check_hook=HAS_OBJECT_PERMISSION),
        "partial_update": IamPermissionInfo(
            IAMMeta.PROJECT_EDIT_ACTION, resource_func, check_hook=HAS_OBJECT_PERMISSION
        ),
    }


class ProjectFilter(AllLookupSupportFilterSet):
    class Meta:
        model = Project
        fields = {
            "id": ALL_LOOKUP,
            "name": ALL_LOOKUP,
            "creator": ALL_LOOKUP,
            "from_cmdb": ALL_LOOKUP,
            "bk_biz_id": ALL_LOOKUP,
            "is_disable": ALL_LOOKUP,
        }


class ProjectSetViewSet(GcloudUpdateViewSet, GcloudListViewSet):
    queryset = Project.objects.all().order_by("-id")
    search_fields = ["id", "name", "desc", "creator"]
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated, ProjectPermission]
    filterset_class = ProjectFilter

    iam_resource_helper = ViewSetResourceHelper(
        resource_func=res_factory.resources_for_project_obj,
        actions=[
            IAMMeta.PROJECT_VIEW_ACTION,
            IAMMeta.PROJECT_EDIT_ACTION,
            IAMMeta.FLOW_CREATE_ACTION,
            IAMMeta.PROJECT_FAST_CREATE_TASK_ACTION,
        ],
    )
