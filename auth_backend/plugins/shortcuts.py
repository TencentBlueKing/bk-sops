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

from ..resources.base import resource_type_lib
from ..backends import get_backend_from_config
from ..exceptions import AuthFailedException
from .utils import build_need_permission

logger = logging.getLogger('root')


def verify_or_return_insufficient_perms(principal_type, principal_id, perms_tuples):
    auth_backend = get_backend_from_config()
    auth_result = auth_backend.verify_multiple_resource_perms(principal_type, principal_id, perms_tuples)

    if not auth_result['result']:
        logger.error('Shortcut verify multiple resource perms failed, return error: {error}'.format(
            error=auth_result['message']
        ))

    if all([item['is_pass'] for item in auth_result['data']]):
        return []

    permissions = []
    for verify_item in [item for item in auth_result['data'] if not item['is_pass']]:
        instance_id = None

        for resource in verify_item['resource_id']:
            if resource['resource_type'] == verify_item['resource_type']:
                instance_id = resource['resource_id']
                break

        permissions.append(build_need_permission(auth_resource=resource_type_lib[verify_item['resource_type']],
                                                 action_id=verify_item['action_id'],
                                                 instance=instance_id))

    return permissions


def batch_verify_or_raise_auth_failed(principal_type, principal_id, perms_tuples, status=499):
    permissions = verify_or_return_insufficient_perms(principal_type, principal_id, perms_tuples)
    if permissions:
        raise AuthFailedException(permissions=permissions, status=status)


def verify_or_raise_auth_failed(principal_type, principal_id, resource, action_ids, instance, status=499):
    batch_verify_or_raise_auth_failed(principal_type,
                                      principal_id,
                                      [(resource, action_ids, instance)],
                                      status)
