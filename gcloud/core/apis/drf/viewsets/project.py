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

from gcloud.contrib.audit.utils import bk_audit_add_event
from gcloud.core.apis.drf.filtersets import ALL_LOOKUP, AllLookupSupportFilterSet
from gcloud.core.apis.drf.permission import HAS_OBJECT_PERMISSION, IamPermission, IamPermissionInfo
from gcloud.core.apis.drf.resource_helpers import ViewSetResourceHelper
from gcloud.core.apis.drf.serilaziers import ProjectSerializer
from gcloud.core.apis.drf.viewsets.base import GcloudListViewSet, GcloudUpdateViewSet
from gcloud.core.models import Project
from gcloud.iam_auth import IAMMeta, res_factory
from gcloud.iam_auth.utils import get_user_projects


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

    def get_queryset(self):
        queryset = super().get_queryset()
        # list 行为原先无任何鉴权(pass_all)，会向任意登录用户暴露全平台项目清单，
        # 这里收敛为当前用户有查看权限的项目，避免跨项目/跨业务项目枚举(信息泄露)
        if getattr(self, "action", None) == "list":
            user_project_ids = list(get_user_projects(self.request.user.username).values_list("id", flat=True))
            queryset = queryset.filter(id__in=user_project_ids)
        return queryset

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        bk_audit_add_event(
            username=request.user.username,
            action_id=IAMMeta.PROJECT_VIEW_ACTION,
            resource_id=IAMMeta.PROJECT_RESOURCE,
            instance=instance,
        )
        return super(ProjectSetViewSet, self).retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        bk_audit_add_event(
            username=request.user.username,
            action_id=IAMMeta.PROJECT_EDIT_ACTION,
            resource_id=IAMMeta.PROJECT_RESOURCE,
            instance=instance,
        )
        return super(ProjectSetViewSet, self).update(request, *args, **kwargs)
