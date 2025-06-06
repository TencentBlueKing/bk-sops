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
from iam import Action, Subject
from iam.contrib.tastypie.shortcuts import allow_or_raise_immediate_response_for_resources_list
from iam.shortcuts import allow_or_raise_auth_failed
from rest_framework import permissions

from gcloud.common_template.models import CommonTemplate
from gcloud.iam_auth import IAMMeta, get_iam_client, res_factory
from gcloud.tasktmpl3.models import TaskTemplate
from gcloud.template_base.models import DefaultTemplateScheme


class TemplatePermissionMixin:
    """
    两种Template统一的鉴权逻辑，需要通过template_type区分
    """

    iam_mapping_config = {
        "project": {
            "delete_action": Action(IAMMeta.FLOW_DELETE_ACTION),
            "resources_list_func": res_factory.resources_list_for_flows,
        },
        "common": {
            "delete_action": Action(IAMMeta.COMMON_FLOW_DELETE_ACTION),
            "resources_list_func": res_factory.resources_list_for_common_flows,
        },
    }

    def has_permission(self, request, view):
        if view.action == "batch_delete":
            self.check_batch_delete_permission(request, view)
        return True

    def check_batch_delete_permission(self, request, view):
        template_ids = request.data.get("template_ids") or []
        tenant_id = request.user.tenant_id
        iam = get_iam_client(tenant_id)
        action = self.iam_mapping_config[self.template_type]["delete_action"]
        resources_list = self.iam_mapping_config[self.template_type]["resources_list_func"](template_ids)
        allow_or_raise_immediate_response_for_resources_list(
            iam=iam,
            system=IAMMeta.SYSTEM_ID,
            subject=Subject("user", request.user.username),
            action=action,
            resources_list=resources_list,
        )


class ProjectTemplatePermission(TemplatePermissionMixin, permissions.BasePermission):
    template_type = "project"


class CommonTemplatePermission(TemplatePermissionMixin, permissions.BasePermission):
    template_type = "common"


class SchemeEditPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.detail:
            return True
        action = "edit" if view.action == "create" else "view"
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
        iam = get_iam_client(tenant_id)
        if template_id is None:
            template_id = data.get("template_id")

        # 项目流程方案的权限控制
        if "project_id" in data or data.get("template_type") != "common":
            # 默认进行是否有流程查看或编辑权限校验
            scheme_action = IAMMeta.FLOW_VIEW_ACTION if action == "view" else IAMMeta.FLOW_EDIT_ACTION
            scheme_resources = res_factory.resources_for_flow(template_id, tenant_id)

        # 公共流程方案的权限控制
        else:
            # 默认进行是否有流程查看或编辑权限校验
            scheme_action = IAMMeta.COMMON_FLOW_VIEW_ACTION if action == "view" else IAMMeta.COMMON_FLOW_EDIT_ACTION
            scheme_resources = res_factory.resources_for_common_flow(template_id, tenant_id)

        allow_or_raise_auth_failed(
            iam=iam,
            system=IAMMeta.SYSTEM_ID,
            subject=Subject("user", request.user.username),
            action=Action(scheme_action),
            resources=scheme_resources,
        )

        return True
