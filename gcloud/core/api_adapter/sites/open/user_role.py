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

import logging

from auth_backend.plugins.constants import PRINCIPAL_TYPE_USER
from blueapps.utils.cache import with_cache

from gcloud.conf import settings
from gcloud.contrib.audit.permissions import audit_center_resource
from gcloud.contrib.function.permissions import function_center_resource

logger = logging.getLogger("root")
CACHE_PREFIX = __name__.replace('.', '_')


def get_operate_user_list(request):
    """
    获取职能化人员列表
    """
    return get_role_user_list('functor')


def get_auditor_user_list(request):
    """
    获取职能化人员列表
    """
    return get_role_user_list('auditor')


@with_cache(settings.DEFAULT_CACHE_TIME_FOR_AUTH, ex=[0, 1])
def get_role_user_list(role):
    if role == 'functor':
        auth_resource = function_center_resource
    else:
        auth_resource = audit_center_resource
    resources_actions = {
        'action_id': auth_resource.actions.view.id,
    }
    search_result = auth_resource.search_resources_perms_principals(resources_actions)
    if not search_result['result']:
        message = ('search perms principals of Resource[{resource}] by backend[{beckend_cls}] '
                   'return error: {error}').format(
            resource=auth_resource.name,
            backend_cls=auth_resource.backend,
            error=search_result['message']
        )
        logger.error(message)
        return []
    perms_principals = search_result['data']
    user_list = [principal['principal_id'] for principal in perms_principals[0]['perms_principals']]
    return user_list


def is_user_functor(request):
    """
    判断是否是职能化人员
    """
    return is_user_role(request.user.username, 'functor')


def is_user_auditor(request):
    """
    判断是否是审计人员
    """
    return is_user_role(request.user.username, 'auditor')


@with_cache(settings.DEFAULT_CACHE_TIME_FOR_AUTH, ex=[0, 1])
def is_user_role(username, role):
    if role == 'functor':
        auth_resource = function_center_resource
    else:
        auth_resource = audit_center_resource
    verify_result = auth_resource.verify_perms(PRINCIPAL_TYPE_USER, username, [auth_resource.actions.view.id])
    if not verify_result['result']:
        message = ('verify perms of Resource[{resource}] by backend[{backend_cls}] '
                   'return error: {error}').format(
            resource=auth_resource.name,
            backend_cls=auth_resource.backend,
            error=verify_result['message']
        )
        logger.error(message)
        return False
    verify_data = verify_result['data']
    for action_resource in verify_data:
        if not action_resource['is_pass']:
            return False
    return True
