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

from django.core.cache import cache

from gcloud.conf import settings
from gcloud import exceptions
from gcloud.core.api_adapter import get_user_info

logger = logging.getLogger("root")
get_client_by_user = settings.ESB_GET_CLIENT_BY_USER
CACHE_PREFIX = __name__.replace('.', '_')
DEFAULT_CACHE_TIME_FOR_CC = settings.DEFAULT_CACHE_TIME_FOR_CC


def get_all_business_list(use_cache=True):
    username = settings.SYSTEM_USE_API_ACCOUNT
    cache_key = "%s_get_all_business_list_%s" % (CACHE_PREFIX, username)
    data = cache.get(cache_key)

    if not (use_cache and data):
        client = get_client_by_user(username)

        result = client.cc.search_business({
            'bk_supplier_account': 0
        })

        if result['result']:
            data = result['data']['info']
            cache.set(cache_key, data, DEFAULT_CACHE_TIME_FOR_CC)
        else:
            raise exceptions.APIError(
                system='cc',
                api='search_business',
                message=result['message']
            )

    return data


# LifeCycle：'1'：测试中， '2'：已上线， '3'： 停运， 其他如'0'、''是非法值
def get_user_business_list(username, use_cache=True):
    """Get authorized business list for a exact username.

    :param object username: User username
    :param bool use_cache: (Optional)
    """
    cache_key = "%s_get_user_business_list_%s" % (CACHE_PREFIX, username)
    data = cache.get(cache_key)

    if not (use_cache and data):
        user_info = _get_user_info(username)
        client = get_client_by_user(username)
        result = client.cc.search_business({
            'bk_supplier_account': user_info['bk_supplier_account'],
            'condition': {'bk_data_status': {'$in': ['enable', 'disabled', None]}}
        })

        if result['result']:
            data = result['data']['info']
            cache.set(cache_key, data, DEFAULT_CACHE_TIME_FOR_CC)
        else:
            raise exceptions.APIError(
                system='cc',
                api='search_business',
                message=result['message'],
                result=result
            )

    return data


def _get_user_info(username, use_cache=True):
    """
    获取用户基本信息
    @param username:
    @param use_cache:
    @return:
    """
    cache_key = "%s_get_user_info_%s" % (CACHE_PREFIX, username)
    data = cache.get(cache_key)
    if not (use_cache and data):
        userinfo = get_user_info(username)
        userinfo.setdefault('code', -1)
        if userinfo['result']:
            data = userinfo['data']
            if data:
                cache.set(cache_key, data, DEFAULT_CACHE_TIME_FOR_CC)
        else:
            raise exceptions.APIError(
                'bk_api',
                'get_user_info',
                userinfo.get('detail_message', userinfo['message'])
            )
    return data


def convert_readable_username(username):
    """将用户名转换成昵称"""
    return username


def convert_group_name(biz_cc_id, role):
    return '%s\x00%s' % (biz_cc_id, role)
