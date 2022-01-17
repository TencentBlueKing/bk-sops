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

from gcloud.iam_auth import IAMMeta

from gcloud.core.models import Project

from ..filter import ALL, QFilterSet
from ..serilaziers import ProjectSerializer
from ..resource_helpers import ResourceHelper
from ..permission import IamResourcesInfo, IamPermissions

from .base import GcloudListViewSet, GcloudUpdateViewSet


class ProjectPermissions(IamPermissions):
    actions = {
        "list": IamResourcesInfo(permission_pass_all=True),
        "update": IamResourcesInfo(
            IAMMeta.PROJECT_EDIT_ACTION, obj_res="resources_for_project_obj", has_permission=False
        ),
        "partial_update": IamResourcesInfo(
            IAMMeta.PROJECT_EDIT_ACTION, obj_res="resources_for_project_obj", has_permission=False
        ),
        "retrieve": IamResourcesInfo(
            IAMMeta.PROJECT_VIEW_ACTION, obj_res="resources_for_project_obj", has_permission=False
        ),
    }


class ProjectFilter(QFilterSet):
    class Meta:
        model = Project
        q_fields = ["id", "name", "desc", "creator"]
        fields = {
            "id": ALL,
            "name": ALL,
            "creator": ALL,
            "from_cmdb": ALL,
            "bk_biz_id": ALL,
            "is_disable": ALL,
        }


class ProjectSetViewSet(GcloudUpdateViewSet, GcloudListViewSet):
    queryset = Project.objects.all().order_by("-id")

    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated, ProjectPermissions]
    filterset_class = ProjectFilter

    iam_resource_helper = ResourceHelper(
        res_type="resources_for_project_obj",
        actions=[
            IAMMeta.PROJECT_VIEW_ACTION,
            IAMMeta.PROJECT_EDIT_ACTION,
            IAMMeta.FLOW_CREATE_ACTION,
            IAMMeta.PROJECT_FAST_CREATE_TASK_ACTION,
        ],
    )
