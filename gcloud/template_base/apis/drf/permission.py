# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from rest_framework import permissions

from gcloud.iam_auth import IAMMeta, get_iam_client, res_factory
from iam import Subject, Action, Request

iam = get_iam_client()


class SchemeEditPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.detail:
            return True
        self.scheme_allow_or_raise_auth_failed(request)
        return True

    def has_object_permission(self, request, view, obj):
        template_id = int(obj.unique_id.split("-")[0])
        self.scheme_allow_or_raise_auth_failed(request, template_id)
        return True

    @staticmethod
    def scheme_allow_or_raise_auth_failed(request, template_id=None):
        data = request.query_params or request.data
        if template_id is None:
            template_id = data.get("template_id")

        # 项目流程方案的权限控制
        if "project_id" in data or data.get("template_type") != "common":
            # 默认进行是否有流程查看权限校验
            scheme_action = IAMMeta.FLOW_VIEW_ACTION
            scheme_resources = res_factory.resources_for_flow(template_id)

        # 公共流程方案的权限控制
        else:
            # 默认进行是否有流程查看权限校验
            scheme_action = IAMMeta.COMMON_FLOW_VIEW_ACTION
            scheme_resources = res_factory.resources_for_common_flow(template_id)

        request = Request(
            IAMMeta.SYSTEM_ID, Subject("user", request.user.username), Action(scheme_action), scheme_resources, None
        )

        return iam.is_allowed_with_cache(request)
