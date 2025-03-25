# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import logging

from django.core.cache import cache

from gcloud import exceptions
from gcloud.conf import settings
from gcloud.core.api_adapter import get_user_info
from gcloud.core.models import EnvironmentVariables

# get_client_by_user = settings.ESB_GET_CLIENT_BY_USER
from packages.bkapi.bk_cmdb.shortcuts import get_client_by_username

logger = logging.getLogger("root")


CACHE_PREFIX = __name__.replace(".", "_")
DEFAULT_CACHE_TIME_FOR_CC = settings.DEFAULT_CACHE_TIME_FOR_CC


def get_all_business_list(use_cache=True):
    username = settings.SYSTEM_USE_API_ACCOUNT
    cache_key = "%s_get_all_business_list_%s" % (CACHE_PREFIX, username)
    data = cache.get(cache_key)

    if not (use_cache and data):
        client = get_client_by_username(username=username, stage=settings.BK_APIGW_STAGE_NAME)

        result = client.api.search_business(
            path_params={
                "bk_supplier_account": EnvironmentVariables.objects.get_var("BKAPP_DEFAULT_SUPPLIER_ACCOUNT", 0)
            },
            headers={"X-Bk-Tenant-Id": "system"},
        )

        if result["result"]:
            data = result["data"]["info"]
            cache.set(cache_key, data, DEFAULT_CACHE_TIME_FOR_CC)
        else:
            raise exceptions.APIError(system="cc", api="search_business", message=result["message"])

    return data


def get_user_business_list(username, tenant_id, use_cache=True):
    """Get authorized business list for a exact username.

    :param object username: User username
    :param bool use_cache: (Optional)
    """
    cache_key = "%s_get_user_business_list_%s" % (CACHE_PREFIX, username)
    data = cache.get(cache_key)

    if not (use_cache and data):
        # user_info = _get_user_info(username, tenant_id)
        client = get_client_by_username(username=username, stage=settings.BK_APIGW_STAGE_NAME)
        result = client.api.search_business(
            path_params={
                "bk_supplier_account": EnvironmentVariables.objects.get_var("BKAPP_DEFAULT_SUPPLIER_ACCOUNT", 0)
            },
            headers={"X-Bk-Tenant-Id": tenant_id},
            params={"condition": {"bk_data_status": {"$in": ["enable", "disabled", None]}}},
        )
        print(tenant_id)
        if result["result"]:
            data = result["data"]["info"]
            cache.set(cache_key, data, DEFAULT_CACHE_TIME_FOR_CC)
        else:
            raise exceptions.APIError(
                system="cc",
                api="search_business",
                message=result.get("message") or result.get("bk_error_msg"),
                result=result,
            )
    return data


def get_user_business_detail(username, bk_biz_id, tenant_id):
    """Get authorized business list for a exact username.

    :param object username: User username
    :param bool use_cache: (Optional)
    """

    # user_info = _get_user_info(username, tenant_id)
    client = get_client_by_username(username=username, stage=settings.BK_APIGW_STAGE_NAME)
    result = client.api.search_business(
        path_params={"bk_supplier_account": EnvironmentVariables.objects.get_var("BKAPP_DEFAULT_SUPPLIER_ACCOUNT", 0)},
        headers={"X-Bk-Tenant-Id": tenant_id},
        params={"condition": {"bk_data_status": {"$in": ["enable", "disabled", None]}, "bk_biz_id": bk_biz_id}},
    )

    if result["result"]:
        data = result["data"]["info"]
    else:
        raise exceptions.APIError(system="cc", api="search_business", message=result["message"], result=result)

    if len(data) != 1:
        raise exceptions.APIError(system="cc", api="search_business", message=result["message"], result=result)

    return data[0]


def _get_user_info(username, tenant_id, use_cache=True):
    """
    获取用户基本信息
    @param username:
    @param use_cache:
    @return:
    """
    cache_key = "%s_get_user_info_%s" % (CACHE_PREFIX, username)
    data = cache.get(cache_key)
    if not (use_cache and data):
        userinfo = get_user_info(username, tenant_id)
        userinfo.setdefault("code", -1)
        if userinfo["result"]:
            data = userinfo["data"]
            if data:
                cache.set(cache_key, data, DEFAULT_CACHE_TIME_FOR_CC)
        else:
            raise exceptions.APIError("bk_api", "get_user_info", userinfo.get("detail_message", userinfo["message"]))
    return data


def convert_readable_username(username):
    """将用户名转换成昵称"""
    return username


def convert_group_name(biz_cc_id, role):
    return "%s\x00%s" % (biz_cc_id, role)
