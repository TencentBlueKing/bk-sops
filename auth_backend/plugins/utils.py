# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from __future__ import absolute_import, unicode_literals

import logging
from builtins import str

import six

from auth_backend.plugins.constants import PRINCIPAL_TYPE_USER
from blueapps.utils.cache import with_cache


logger = logging.getLogger('root')
CACHE_PREFIX = __name__.replace('.', '_')


def build_need_permission(auth_resource, action_id, instance=None, scope_id=None):
    base_info = auth_resource.base_info()
    resource = base_info.pop('resource')
    resources = []
    if instance is not None:
        resource_id = instance if isinstance(instance, (six.string_types, int)) else auth_resource.resource_id(instance)
        resource.update({
            'resource_id': resource_id,
            'resource_name': auth_resource.resource_name(instance)
        })
        resources.append([resource])

    base_info.update({
        'resource_type': resource['resource_type'],
        'resource_type_name': resource['resource_type_name'],
        'action_id': action_id,
        'scope_id': scope_id or base_info['scope_id'],
        'action_name': auth_resource.actions_map[action_id].name,
        'resources': resources
    })
    return base_info


@with_cache(seconds=10,
            prefix='{}_search_all_resources_authorized_actions'.format(CACHE_PREFIX),
            ex=['username', 'resource_type', 'action_ids'])
def search_all_resources_authorized_actions(username, resource_type, auth_resource, action_ids=None, scope_id=None):
    """
    @summary: 获取所有用户对某个资源类型的所有资源实例的权限
    @param username:
    @param resource_type: 资源类型，这里仅用作缓存with_cache关键字
    @param auth_resource:
    @param action_ids:
    @param scope_id:
    @return:
    """
    if action_ids is None:
        action_ids = list(auth_resource.actions_map.keys())
    authorized_result = auth_resource.backend.search_authorized_resources(
        resource=auth_resource,
        principal_type=PRINCIPAL_TYPE_USER,
        principal_id=username,
        action_ids=action_ids,
        scope_id=scope_id)
    if not authorized_result['result']:
        logger.error("Search authorized resources of Resource[{resource}] return error: {error}".format(
            resource=auth_resource.name,
            error=authorized_result['message']
        ))
        return {}
    authorized_resources = authorized_result['data']
    resources_perms = {}
    for action_resource in authorized_resources:
        for absolute_resource in action_resource['resource_ids']:
            for relative_resource in absolute_resource:
                if relative_resource['resource_type'] == auth_resource.rtype:
                    resource_id = str(relative_resource['resource_id'])
                    resources_perms.setdefault(resource_id, []).append(action_resource['action_id'])
    return resources_perms


@with_cache(seconds=10,
            prefix='{}_search_instance_authorized_actions'.format(CACHE_PREFIX),
            ex=['username', 'resource_type', 'instance_id', 'action_ids'])
def search_instance_authorized_actions(
    username,
    resource_type,
    auth_resource,
    instance_id,
    instance,
    action_ids=None,
    scope_id=None
):
    if action_ids is None:
        action_ids = list(auth_resource.actions_map.keys())
    verify_result = auth_resource.backend.verify_perms(
        resource=auth_resource,
        principal_type=PRINCIPAL_TYPE_USER,
        principal_id=username,
        action_ids=action_ids,
        instance=instance,
        scope_id=scope_id
    )
    if not verify_result['result']:
        logger.error("Search authorized actions of Resource[{resource}] return error: {error}".format(
            resource=auth_resource.name,
            error=verify_result['message']
        ))
        return []

    authorized_actions = []
    for action_info in verify_result['data']:
        if action_info['is_pass']:
            authorized_actions.append(action_info['action_id'])

    return authorized_actions
