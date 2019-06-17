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

import logging

from blueapps.utils.cache import with_cache

from ..constants import PRINCIPAL_TYPE_USER

logger = logging.getLogger('root')
CACHE_PREFIX = __name__.replace('.', '_')


class BkSaaSLabeledDataResourceMixin(object):
    def dehydrate(self, bundle):
        username = bundle.request.user.username
        auth_resource = getattr(self._meta, 'auth_resource', None)
        auth_operations = getattr(self._meta, 'auth_operations', None)
        if auth_resource is None or auth_operations is None:
            return bundle

        resources_perms = search_all_resources_authorized_actions(username, auth_resource.rtype, auth_resource)
        auth_actions = resources_perms.get(str(bundle.obj.pk), [])
        bundle.data['auth_actions'] = auth_actions
        bundle.data['auth_operations'] = auth_operations
        return bundle


@with_cache(seconds=10, prefix=CACHE_PREFIX, ex=[0, 1])
def search_all_resources_authorized_actions(username, resource_type, auth_resource):
    """
    @summary: 获取所有用户对所有资源的权限
    @param username:
    @param resource_type: 资源类型，这里仅用作缓存with_cache关键字
    @param auth_resource:
    @return:
    """
    authorized_result = auth_resource.backend.search_authorized_resources(
        resource=auth_resource,
        principal_type=PRINCIPAL_TYPE_USER,
        principal_id=username,
        action_ids=auth_resource.actions_map.keys())
    if not authorized_result['result']:
        logger.error('Search authorized resources of Resource[{resource}] return error: {error}'.format(
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
