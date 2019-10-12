# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from __future__ import absolute_import, unicode_literals

import abc

from builtins import object
from future.utils import with_metaclass


class AuthBackend(with_metaclass(abc.ABCMeta, object)):
    @abc.abstractmethod
    def register_instance(self, resource, instance, scope_id=None):
        """
        向权限系统注册实例
        :param resource: 实例对应的资源对象
        :param instance: 资源实例
        :param scope_id: 作用域 ID
        :return:
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def batch_register_instance(self, resource, instances, scope_id=None):
        """
        向权限系统批量注册实例
        :param resource: 实例对应的资源对象
        :param instances: 资源实例列表
        :param scope_id: 作用域 ID
        :return:
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def update_instance(self, resource, instance, scope_id=None):
        """
        更新权限系统中的实例信息
        :param resource: 实例对应的资源对象
        :param instance: 资源实例
        :param scope_id: 作用域 ID
        :return:
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def delete_instance(self, resource, instance, scope_id=None):
        """
        删除注册在权限系统中的实例
        :param resource: 实例对应的资源对象
        :param instance: 资源实例
        :param scope_id: 作用域 ID
        :return:
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def batch_delete_instance(self, resource, instances, scope_id=None):
        """
        批量删除注册在权限系统中的实例
        :param resource: 实例对应的资源对象
        :param instances: 资源实例列表
        :param scope_id: 作用域 ID
        :return:
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def verify_perms(self, principal_type, principal_id, resource, action_ids, instance=None, scope_id=None):
        """
        校验主体是否拥有某个资源下的某些操作权限
        :param principal_type: 主体类型
        :param principal_id: 主体 ID
        :param resource: 资源对象
        :param action_ids: 资源对象中的操作 ID
        :param instance: 关联实例的操作中所关联的实例
        :param scope_id: 作用域 ID
        :return:
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def batch_verify_perms(self, principal_type, principal_id, resource, action_ids, instances=None, scope_id=None):
        """
        批量校验主体是否拥有某个资源下的某些操作权限
        :param principal_type: 主体类型
        :param principal_id: 主体 ID
        :param resource: 资源对象
        :param action_ids: 资源对象中的操作 ID
        :param instances: 关联实例的操作中所关联的实例
        :param scope_id: 作用域 ID
        :return:
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def verify_multiple_resource_perms(self, principal_type, principal_id, perms_tuples, scope_id=None):
        """
        批量校验主体是否有某几个同作用域下的资源的某些操作权限
        :param principal_type: 主体类型
        :param principal_id: 主体 ID
        :param perms_tuples: 待校验权限元组 (资源对象, [操作 ID 列表], 资源实例)
        :param scope_id: 作用域 ID
        :return:
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def search_authorized_resources(self, resource, principal_type, principal_id, action_ids, scope_id=None):
        """
        批量查询有权限的资源
        :param resource: 资源对象
        :param principal_type: 主题类型
        :param principal_id: 主题 ID
        :param action_ids: 资源对象中的操作 ID
        :param scope_id: 作用域 ID
        :return:
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def search_resources_perms_principals(self, resource, resources_actions, scope_id=None):
        """

        :param resource: 资源对象
        :param resources_actions: 资源操作列表
        :param scope_id: 作用域 ID
        :return:
        """
        raise NotImplementedError()
