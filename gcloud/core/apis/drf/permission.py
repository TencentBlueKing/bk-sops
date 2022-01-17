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


class IamResourcesInfo(object):
    def __init__(
        self,
        iam_action=None,
        res=None,
        id_field="id",
        obj_res=None,
        permission_pass_all=False,
        has_permission=True,
        has_object_permission=True,
    ):
        """
        :param iam_action: 权限类型
        :param res: has_permission中需要校验的资源，需要在res_factory模块中定义
        :param id_field: 资源指定字段，会从request中获取，然后被 res　调用， 从request中获取失败时，抛出 PermissionDenied 异常
        :param obj_res: has_object_permission 从使用的资源，需要在res_factory模块中定义，调用obj对象
        :param permission_pass_all: 行为不做校验，直接通过，优先级最高
        :param has_permission: has_permission 启用
        :param has_object_permission: has_object_permission 启用
        """
        self.iam_action = iam_action
        self.permission_pass_all = permission_pass_all
        if self.permission_pass_all:
            return
        if has_permission and not res:
            raise NotImplementedError("has_permission为true时，参数res不能为空")
        self.res = res
        self.id_field = id_field
        if has_object_permission and not obj_res:
            raise NotImplementedError("has_object_permission 为true时，参数obj_res不能为空")
        self.obj_res = obj_res


class IamPermissions(IAMMixin, permissions.BasePermission):
    """
    未出现在actions中的行为不被允许
    """

    actions = {}

    def get_id_field(self, request, id_field):
        id_field = request.query_params.get(id_field) or request.data.get(id_field)
        if id_field is None:
            raise PermissionDenied
        return id_field

    def has_permission(self, request, view):
        if view.action in self.actions:
            res_info = self.actions[view.action]
            if res_info.permission_pass_all:
                return True

            if res_info.res:
                resources = getattr(res_factory, res_info.res)(self.get_id_field(request, res_info.id_field))
                self.iam_auth_check(request, action=res_info.res, resources=resources)
            return True
        else:
            raise PermissionDenied

    def has_object_permission(self, request, view, obj):
        if view.action in self.actions:
            res_info = self.actions[view.action]
            if res_info.permission_pass_all:
                return True

            if res_info.obj_res:
                resources = getattr(res_factory, res_info.obj_res)(obj)
                self.iam_auth_check(request, action=res_info.obj_res, resources=resources)
            return True
        else:
            raise PermissionDenied
