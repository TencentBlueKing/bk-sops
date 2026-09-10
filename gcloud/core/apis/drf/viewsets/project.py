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
from django.conf import settings
from rest_framework import permissions

from gcloud.contrib.audit.utils import bk_audit_add_event
from gcloud.core.apis.drf.filtersets import ALL_LOOKUP, AllLookupSupportFilterSet
from gcloud.core.apis.drf.permission import HAS_OBJECT_PERMISSION, IamPermission, IamPermissionInfo
from gcloud.core.apis.drf.resource_helpers import ViewSetResourceHelper
from gcloud.core.apis.drf.serilaziers import ProjectSerializer
from gcloud.core.apis.drf.viewsets.base import GcloudListViewSet, GcloudUpdateViewSet
from gcloud.core.models import Project
from gcloud.iam_auth import IAMMeta, get_iam_client, res_factory
from gcloud.iam_auth.exceptions import IAMPermissionDenied
from gcloud.iam_auth.service import PermissionService
from gcloud.iam_auth.types import PermissionCheck
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

    def has_object_permission(self, request, view, obj):
        if view.action not in {"retrieve", "detail"}:
            return super().has_object_permission(request, view, obj)

        resource = type(self).resource_func(obj, request.user.tenant_id)[0]
        action_ids = [IAMMeta.PROJECT_VIEW_ACTION, IAMMeta.PROJECT_COMMON_CREATE_TASK_ACTION]
        decisions = PermissionService().allowed_actions(
            request.user.username, request.user.tenant_id, action_ids, resource
        )
        if any(decisions.values()):
            return True

        reexecute_task_id = request.query_params.get("reexecute_task_id")
        if reexecute_task_id:
            # “再次执行”需要项目基础上下文，但不应把 project_view 作为额外前置权限。
            # 必须先确认原任务属于当前租户和项目，再复用 task_view（含创建人兼容）校验。
            from gcloud.taskflow3.models import TaskFlowInstance

            task_exists = TaskFlowInstance.objects.filter(
                id=reexecute_task_id,
                project_id=obj.id,
                project__tenant_id=request.user.tenant_id,
                is_deleted=False,
            ).exists()
            if task_exists:
                task_resources = res_factory.resources_for_task(reexecute_task_id, request.user.tenant_id)
                if task_resources and PermissionService().is_allowed(
                    request.user.username,
                    request.user.tenant_id,
                    PermissionCheck(IAMMeta.TASK_VIEW_ACTION, task_resources[0]),
                ):
                    return True

        # 保持原有无权限提示：普通项目详情仍申请 project_view，不向用户展示二选一权限。
        raise IAMPermissionDenied([PermissionCheck(IAMMeta.PROJECT_VIEW_ACTION, resource)])


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
    model_multi_tenant_filter = settings.ENABLE_MULTI_TENANT_MODE

    @staticmethod
    def iam_resource_helper(tenant_id):
        iam_client = get_iam_client(tenant_id=tenant_id)
        return ViewSetResourceHelper(
            iam=iam_client,
            resource_func=res_factory.resources_for_project_obj,
            actions=[
                IAMMeta.PROJECT_VIEW_ACTION,
                IAMMeta.PROJECT_EDIT_ACTION,
                IAMMeta.FLOW_CREATE_ACTION,
                IAMMeta.PROJECT_FAST_CREATE_TASK_ACTION,
                IAMMeta.PROJECT_COMMON_CREATE_TASK_ACTION,
            ],
        )

    def get_queryset(self):
        queryset = super().get_queryset()
        # list 行为原先无任何鉴权(pass_all)，会向任意登录用户暴露全平台项目清单，
        # 这里收敛为当前用户有查看权限的项目，避免跨项目/跨业务项目枚举(信息泄露)
        if getattr(self, "action", None) == "list":
            user_project_ids = list(
                get_user_projects(self.request.user.username, self.request.user.tenant_id).values_list("id", flat=True)
            )
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
