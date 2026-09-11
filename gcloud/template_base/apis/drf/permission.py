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
from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied

from gcloud.common_template.models import CommonTemplate
from gcloud.iam_auth import IAMMeta, PermissionService, get_iam_client, res_factory
from gcloud.iam_auth.creator import is_flow_creator
from gcloud.iam_auth.models import Action, Subject
from gcloud.iam_auth.shortcuts import allow_or_raise_auth_failed
from gcloud.tasktmpl3.models import TaskTemplate
from gcloud.template_base.models import DefaultTemplateScheme


class TemplatePermissionMixin:
    """
    两种Template统一的鉴权逻辑，需要通过template_type区分
    """

    iam_mapping_config = {
        "project": {
            "delete_action": Action(IAMMeta.FLOW_DELETE_ACTION),
            "model": TaskTemplate,
            "tenant_filter": "project__tenant_id",
            "resource_func": res_factory.resources_for_flow_obj,
        },
        "common": {
            "delete_action": Action(IAMMeta.COMMON_FLOW_DELETE_ACTION),
            "model": CommonTemplate,
            "tenant_filter": "tenant_id",
            "resource_func": res_factory.resources_for_common_flow_obj,
        },
    }

    def has_permission(self, request, view):
        if view.action == "batch_delete":
            self.check_batch_delete_permission(request, view)
        return True

    def check_batch_delete_permission(self, request, view):
        serializer = view.template_ids_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        template_ids = serializer.validated_data["template_ids"]
        tenant_id = request.user.tenant_id
        config = self.iam_mapping_config[self.template_type]
        templates = list(
            config["model"]
            .objects.select_related("pipeline_template")
            .filter(id__in=template_ids, is_deleted=False, **{config["tenant_filter"]: tenant_id})
        )
        if len(templates) != len(template_ids):
            # Do not expose whether an ID belongs to another tenant or does not exist.
            raise PermissionDenied("template does not exist in current tenant")
        resources = [config["resource_func"](template)[0] for template in templates]
        PermissionService().require_resources(
            request.user.username,
            tenant_id,
            config["delete_action"].id,
            resources,
        )
        request._authorized_batch_delete_template_ids = template_ids


class ProjectTemplatePermission(TemplatePermissionMixin, permissions.BasePermission):
    template_type = "project"


class CommonTemplatePermission(TemplatePermissionMixin, permissions.BasePermission):
    template_type = "common"


class SchemeEditPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.detail:
            return True
        # batch_operate 会批量创建/更新/删除执行方案，属于写操作，需校验编辑权限，
        # 避免仅有查看权限的用户越权修改方案
        action = "edit" if view.action in ("create", "batch_operate") else "view"
        self.scheme_allow_or_raise_auth_failed(request, action=action)
        return True

    def has_object_permission(self, request, view, obj):
        data = request.query_params or request.data
        # 项目流程方案的权限控制
        if "project_id" in data or data.get("template_type") != "common":
            model_cls = TaskTemplate
        # 公共流程方案的权限控制
        else:
            model_cls = CommonTemplate

        template_id = (
            obj.template_id
            if isinstance(obj, DefaultTemplateScheme)
            else model_cls.objects.filter(pipeline_template__id=obj.template_id).values_list("id", flat=True)[0]
        )
        action = "edit" if view.action in ["update", "partial_update", "destroy"] else "view"
        self.scheme_allow_or_raise_auth_failed(request, template_id, action=action)
        return True

    @staticmethod
    def scheme_allow_or_raise_auth_failed(request, template_id=None, action="view"):
        data = request.query_params or request.data
        tenant_id = request.user.tenant_id
        if template_id is None:
            template_id = data.get("template_id")

        # 项目流程方案的权限控制
        if "project_id" in data or data.get("template_type") != "common":
            if is_flow_creator(
                request.user.username,
                tenant_id,
                template_id,
                project_id=data.get("project_id"),
            ):
                return True
            # 默认进行是否有流程查看或编辑权限校验
            scheme_action = IAMMeta.FLOW_VIEW_ACTION if action == "view" else IAMMeta.FLOW_EDIT_ACTION
            scheme_resources = res_factory.resources_for_flow(template_id, tenant_id)

        # 公共流程方案的权限控制
        else:
            # 默认进行是否有流程查看或编辑权限校验
            scheme_action = IAMMeta.COMMON_FLOW_VIEW_ACTION if action == "view" else IAMMeta.COMMON_FLOW_EDIT_ACTION
            scheme_resources = res_factory.resources_for_common_flow(template_id, tenant_id)

        iam = get_iam_client(tenant_id)
        allow_or_raise_auth_failed(
            iam=iam,
            system=IAMMeta.SYSTEM_ID,
            subject=Subject("user", request.user.username),
            action=Action(scheme_action),
            resources=scheme_resources,
        )

        return True
