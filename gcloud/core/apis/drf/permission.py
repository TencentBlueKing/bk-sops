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

from gcloud.core.apis.drf.viewsets import IAMMixin


class IamPermissionInfo:
    def __init__(
        self,
        iam_action=None,
        resource_func=None,
        id_field="id",
        pass_all=False,
        to_permission="resource",
    ):
        """
        :param iam_action: 权限类型
        :param resource_func: has_permission中需要校验的资源，需要在res_factory模块中定义函数,默认为[]
        :param id_field: 资源指定字段，会从request中获取，然后被 res　调用， 从request中获取失败时，抛出 PermissionDenied 异常
        :param pass_all: 行为不做校验，直接通过，优先级最高
        :param to_permission: object 或者 resource , 为resource时执行has_permission, object时执行has_object_permission
        """
        self.iam_action = iam_action
        self.pass_all = pass_all
        self.to_permission = to_permission
        self.resource_func = resource_func if resource_func else []
        self.id_field = id_field


class IamPermission(IAMMixin, permissions.BasePermission):

    actions = {}

    def get_id_field(self, request, id_field):
        id_field = request.query_params.get(id_field) or request.data.get(id_field)
        if id_field is None:
            raise PermissionDenied
        return id_field

    def check_permission(self, request, view, resource_param=None, permission_from=None):

        # 未出现在actions中的行为不被允许
        if view.action not in self.actions:
            raise PermissionDenied

        permission_info = self.actions[view.action]

        # 不做权限校验
        if permission_info.pass_all:
            return True

        # 匹配权限校验
        if permission_info.to_permission == permission_from:
            if permission_from == "resource":
                resource_param = self.get_id_field(request, permission_info.id_field)

            resources = []
            if permission_info.resource_func:
                resources = permission_info.resource_func(resource_param)
            self.iam_auth_check(request, action=permission_info.iam_action, resources=resources)
        return True

    def has_permission(self, request, view):
        return self.check_permission(request, view, permission_from="resource")

    def has_object_permission(self, request, view, obj):
        return self.check_permission(request, view, obj, "object")
