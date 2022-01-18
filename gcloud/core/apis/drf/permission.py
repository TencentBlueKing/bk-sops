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
from rest_framework.exceptions import PermissionDenied

from gcloud.iam_auth import res_factory
from gcloud.core.apis.drf.viewsets import IAMMixin


class IamPermissionInfo(object):
    def __init__(
        self,
        iam_action=None,
        res=None,
        id_field="id",
        obj_res=None,
        pass_all=False,
        has_permission=True,
        has_object_permission=True,
    ):
        """
        :param iam_action: 权限类型
        :param res: has_permission中需要校验的资源，需要在res_factory模块中定义,默认为[]
        :param id_field: 资源指定字段，会从request中获取，然后被 res　调用， 从request中获取失败时，抛出 PermissionDenied 异常
        :param obj_res: has_object_permission 从使用的资源，需要在res_factory模块中定义，调用obj对象, 默认为[]
        :param pass_all: 行为不做校验，直接通过，优先级最高
        :param has_permission: has_permission 启用
        :param has_object_permission: has_object_permission 启用
        """
        self.iam_action = iam_action
        self.pass_all = pass_all
        self.has_permission = has_permission
        self.res = res if res else []
        self.id_field = id_field
        self.has_object_permission = has_object_permission
        self.obj_res = obj_res if obj_res else []


class IamPermission(IAMMixin, permissions.BasePermission):
    """
    未出现在actions中的行为不被允许
    """

    actions = {}

    def get_id_field(self, request, id_field):
        id_field = request.query_params.get(id_field) or request.data.get(id_field)
        if id_field is None:
            raise PermissionDenied
        return id_field

    def check_permission(self, request, iam_action, res, res_params=None):
        resources = []
        if res:
            param = self.get_id_field(request, res_params) if isinstance(res_params, str) else res_params
            resources = getattr(res_factory, res)(param)
        self.iam_auth_check(request, action=iam_action, resources=resources)

    def has_permission(self, request, view):
        if view.action in self.actions:
            permission_info = self.actions[view.action]
            # 允许所有
            if permission_info.pass_all:
                return True

            iam_action = permission_info.iam_action
            resource = permission_info.res
            if permission_info.has_permission:
                self.check_permission(request, iam_action, resource, permission_info.id_field)
            return True
        else:
            raise PermissionDenied

    def has_object_permission(self, request, view, obj):
        if view.action in self.actions:
            permission_info = self.actions[view.action]
            # 允许所有
            if permission_info.pass_all:
                return True

            iam_action = permission_info.iam_action
            resource = permission_info.obj_res
            if permission_info.has_object_permission:
                self.check_permission(request, iam_action, resource, obj)
            return True
        else:
            raise PermissionDenied
