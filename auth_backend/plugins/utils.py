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


def build_need_permission(auth_resource, action_id, instance=None):
    resource = {
        'resource_type': auth_resource.rtype,
        'resource_type_name': auth_resource.name,
    }
    if instance is not None:
        resource_id = instance if isinstance(instance, (basestring, int)) else auth_resource.resource_id(instance)
        resource.update({
            'resource_id': resource_id,
            'resource_name': auth_resource.resource_name(instance)
        })
    return {
        'system_id': auth_resource.backend.client.system_id,
        'system_name': auth_resource.backend.client.system_name,
        'scope_type': auth_resource.scope_type,
        'scope_id': auth_resource.scope_id,
        'scope_name': auth_resource.scope_name,
        'action_id': action_id,
        'action_name': auth_resource.actions_map[action_id].name,
        'resources': [
            [
                resource
            ]
        ]
    }
