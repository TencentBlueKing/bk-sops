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

import abc


class AuthBackend(object):
    __metaclass__ = abc.ABCMeta

    def register_instance(self, resource, instance):
        """
        向权限系统注册实例
        :param resource: 实例对应的资源对象
        :param instance: 资源实例
        :return:
        """
        raise NotImplementedError()

    def batch_register_instance(self, resource, instances):
        """
        向权限系统批量注册实例
        :param resource: 实例对应的资源对象
        :param instances: 资源实例列表
        :return:
        """
        raise NotImplementedError()

    def update_instance(self, resource, instance):
        """
        更新权限系统中的实例信息
        :param resource: 实例对应的资源对象
        :param instance: 资源实例
        :return:
        """
        raise NotImplementedError()

    def delete_instance(self, resource, instance):
        """
        删除注册在权限系统中的实例
        :param resource: 实例对应的资源对象
        :param instance: 资源实例
        :return:
        """
        raise NotImplementedError()

    def batch_delete_instance(self, resource, instances):
        """
        批量删除注册在权限系统中的实例
        :param resource: 实例对应的资源对象
        :param instances: 资源实例列表
        :return:
        """
        raise NotImplementedError()

    def verify_perms(self, principal_type, principal_id, resource, action_ids, instance=None):
        """
        校验主体是否拥有某个资源下的某些操作权限
        :param principal_type: 主体类型
        :param principal_id: 主体 ID
        :param resource: 资源对象
        :param action_ids: 资源对象中的操作 ID
        :param instance: 关联实例的操作中所关联的实例
        :return:
        """
        raise NotImplementedError()

    def batch_verify_perms(self, principal_type, principal_id, resource, action_ids, instances=None):
        """
        校验主体是否拥有某个资源下的某些操作权限
        :param principal_type: 主体类型
        :param principal_id: 主体 ID
        :param resource: 资源对象
        :param action_ids: 资源对象中的操作 ID
        :param instances: 关联实例的操作中所关联的实例
        :return:
        """
        raise NotImplementedError()

    def verify_multi_resource_perms(self, principal_type, principal_id, resource_actions):
        """
        校验主体是否拥有多种资源下的某些不关联资源的操作权限
        :param principal_type: 主体类型
        :param principal_id: 主体 ID
        :param resource_actions: 资源类型 ID : [actions_id] 的字典
        :return:
        """
        raise NotImplementedError()
