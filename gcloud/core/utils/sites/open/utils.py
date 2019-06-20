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

import json
import logging

from django.core.cache import cache

from gcloud.conf import settings
from gcloud import exceptions
from gcloud.core.constant import AE
from gcloud.core.api_adapter import get_user_info

logger = logging.getLogger("root")
get_client_by_request = settings.ESB_GET_CLIENT_BY_REQUEST
get_client_by_user = settings.ESB_GET_CLIENT_BY_USER
CACHE_PREFIX = __name__.replace('.', '_')
DEFAULT_CACHE_TIME_FOR_CC = settings.DEFAULT_CACHE_TIME_FOR_CC


# LifeCycle：'1'：测试中， '2'：已上线， '3'： 停运， 其他如'0'、''是非法值
def get_user_business_list(request, use_cache=True):
    """Get authorized business list for a exact username.

    :param object request: django request object.
    :param bool use_cache: (Optional)
    """
    user = request.user
    cache_key = "%s_get_user_business_list_%s" % (CACHE_PREFIX, user.username)
    data = cache.get(cache_key)

    if not (use_cache and data):
        user_info = _get_user_info(request)
        client = get_client_by_request(request)
        result = client.cc.search_business({
            'bk_supplier_account': user_info['bk_supplier_account'],
            'condition': {
                'bk_data_status': {'$in': ['enable', 'disabled', None]},
                '$or': [{'bk_biz_developer': {"$regex": user.username}},
                        {'bk_biz_productor': {"$regex": user.username}},
                        {'bk_biz_maintainer': {"$regex": user.username}},
                        {'bk_biz_tester': {"$regex": user.username}}]
            }
        })

        if result['result']:
            data = result['data']['info']
            cache.set(cache_key, data, DEFAULT_CACHE_TIME_FOR_CC)
        elif result.get('code') in ('20101', 20101):
            raise exceptions.Unauthorized(result['message'])
        elif result.get('code') in ('20103', 20103, '20201', 20201,
                                    '20202', 20202):
            raise exceptions.Forbidden(result['message'])
        else:
            raise exceptions.APIError(
                'cc',
                'search_business',
                result
            )

    return data


def _get_user_info(request, use_cache=True):
    """
    获取用户基本信息
    @param request:
    @param use_cache:
    @return:
    """
    user = request.user
    cache_key = "%s_get_user_info_%s" % (CACHE_PREFIX, user.username)
    data = cache.get(cache_key)
    if not (use_cache and data):
        userinfo = get_user_info(request)
        userinfo.setdefault('code', -1)
        if userinfo['result']:
            data = userinfo['data']
            if data:
                cache.set(cache_key, data, DEFAULT_CACHE_TIME_FOR_CC)
        elif userinfo.get('code') in ('20101', 20101):
            raise exceptions.Unauthorized(userinfo['message'])
        elif userinfo.get('code') in ('20103', 20103, '20201', 20201,
                                      '20202', 20202):
            raise exceptions.Forbidden(userinfo['message'])
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


def check_and_rename_params(conditions, group_by, group_by_check=AE.group_list):
    """
    检验参数是否正确
    :param conditions:参数是一个dict
    :param group_by:分组凭据
    :param group_by_check:分组检查内容
    :return:
    """
    # conditions 是否是一个dict.
    # 本地测试时请注释该try
    result_dict = {'success': False, 'content': None, "conditions": conditions, "group_by": None}
    try:
        conditions = json.loads(conditions)
    except Exception:
        message = u"param conditions[%s] cannot be converted to dict" % conditions
        logger.error(message)
        result_dict['content'] = message
        return result_dict
    if not isinstance(conditions, dict):
        message = u"params conditions[%s] are invalid dict data" % conditions
        logger.error(message)
        result_dict['content'] = message
        return result_dict
    # 检查传递分组是否有误
    if group_by not in group_by_check:
        message = u"params group_by[%s] is invalid" % group_by
        logger.error(message)
        result_dict['content'] = message
        return result_dict

    result_dict['success'] = True
    result_dict['group_by'] = group_by
    result_dict['conditions'] = conditions
    return result_dict


def convert_group_name(biz_cc_id, role):
    return '%s\x00%s' % (biz_cc_id, role)
