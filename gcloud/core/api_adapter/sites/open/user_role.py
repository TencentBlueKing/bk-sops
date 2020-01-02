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

from django.core.cache import cache

from gcloud.conf import settings


logger = logging.getLogger("root")
CACHE_PREFIX = __name__.replace('.', '_')
ROLE_MAPS = {
    'functor': 3,
    'auditor': 4
}
get_client_by_user = settings.ESB_GET_CLIENT_BY_USER


def get_operate_user_list(request):
    """
    获取职能化人员列表
    """
    return get_role_user_list(request, 'functor')


def get_auditor_user_list(request):
    """
    获取职能化人员列表
    """
    return get_role_user_list(request, 'auditor')


def get_role_user_list(request, role):
    if role not in ROLE_MAPS:
        return []
    cache_key = "%s_get_%s_user_list" % (CACHE_PREFIX, role)
    user_list = cache.get(cache_key)

    if user_list is None:
        client = get_client_by_user(request.user.username)
        auth = getattr(client, settings.ESB_AUTH_COMPONENT_SYSTEM)
        result = auth.get_all_users(
            {'bk_role': ROLE_MAPS[role]}
        )
        if result['result']:
            user_list = [user['bk_username'] for user in result['data']]
        else:
            logger.warning('client.%s.get_all_user error: %s' % (
                settings.ESB_AUTH_COMPONENT_SYSTEM,
                result))
            user_list = []
        cache.set(cache_key, user_list, settings.DEFAULT_CACHE_TIME_FOR_AUTH)

    return user_list


def is_user_functor(request):
    """
    判断是否是职能化人员
    """
    return is_user_role(request, 'functor')


def is_user_auditor(request):
    """
    判断是否是审计人员
    """
    return is_user_role(request, 'auditor')


def is_user_role(request, role):
    if role not in ROLE_MAPS:
        return False
    cache_key = "%s_is_user_%s_%s" % (CACHE_PREFIX, role, request.user.username)
    is_role = cache.get(cache_key)

    if is_role is None:
        client = get_client_by_user(request.user.username)
        auth = getattr(client, settings.ESB_AUTH_COMPONENT_SYSTEM)
        get_user_info = getattr(auth, settings.ESB_AUTH_GET_USER_INFO)
        result = get_user_info({})
        if result['result'] and result['data']['bk_role'] == ROLE_MAPS[role]:
            is_role = True
        else:
            is_role = False
        cache.set(cache_key, is_role, settings.DEFAULT_CACHE_TIME_FOR_AUTH)

    return is_role


if __name__ == '__main__':
    test_result = get_operate_user_list()
    print repr(test_result)
