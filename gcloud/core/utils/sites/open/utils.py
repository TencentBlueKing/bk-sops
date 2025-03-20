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

from packages.bkapi.bk_cmdb.shortcuts import get_client_by_username
from gcloud.conf import settings
from gcloud import exceptions
from gcloud.core.models import EnvironmentVariables
from gcloud.core.api_adapter import get_user_info

logger = logging.getLogger("root")
CACHE_PREFIX = __name__.replace(".", "_")
DEFAULT_CACHE_TIME_FOR_CC = settings.DEFAULT_CACHE_TIME_FOR_CC


def get_all_business_list(use_cache=True, tenant_id: str = None):
    username = settings.SYSTEM_USE_API_ACCOUNT
    cache_key = "%s_get_all_business_list_%s" % (CACHE_PREFIX, username)
    data = cache.get(cache_key)

    if not (use_cache and data):
        bk_supplier_account = EnvironmentVariables.objects.get_var("BKAPP_DEFAULT_SUPPLIER_ACCOUNT", 0)
        client = get_client_by_username(username, stage=settings.BK_APIGW_STAGE_NAME)

        result = client.api.search_business(
            {"bk_supplier_account": bk_supplier_account},
            path_params={"bk_supplier_account": bk_supplier_account},
            headers={"X-Bk-Tenant-Id": tenant_id}
        )

        if result["result"]:
            data = result["data"]["info"]
            cache.set(cache_key, data, DEFAULT_CACHE_TIME_FOR_CC)
        else:
            raise exceptions.APIError(system="cc", api="search_business", message=result["message"])

    return data


def get_user_business_list(tenant_id, username, use_cache=True):
    """Get authorized business list for a exact username.

    :param str tenant_id: 租户 ID
    :param object username: User username
    :param bool use_cache: (Optional)
    :param str tenant_id: (Optional)
    """
    cache_key = "%s_get_user_business_list_%s_%s" % (CACHE_PREFIX, username, tenant_id)
    data = cache.get(cache_key)

    if not (use_cache and data):
        client = get_client_by_username(username, stage=settings.BK_APIGW_STAGE_NAME)
        bk_supplier_account = EnvironmentVariables.objects.get_var("BKAPP_DEFAULT_SUPPLIER_ACCOUNT", 0)
        result = client.api.search_business(
            data={
                "bk_supplier_account": bk_supplier_account,
                "condition": {"bk_data_status": {"$in": ["enable", "disabled", None]}},
            },
            path_params={"bk_supplier_account": bk_supplier_account},
            headers={"X-Bk-Tenant-Id": tenant_id},
        )

        if result["result"]:
            data = result["data"]["info"]
            cache.set(cache_key, data, DEFAULT_CACHE_TIME_FOR_CC)
        else:
            raise exceptions.APIError(system="cc", api="search_business", message=result["message"], result=result)

    return data


def get_user_business_detail(tenant_id, username, bk_biz_id):
    """Get authorized business list for a exact username.

    :param str tenant_id: (Optional)
    :param object username: User username
    :param int bk_biz_id: (Optional)
    """
    client = get_client_by_username(username, stage=settings.BK_APIGW_STAGE_NAME)
    bk_supplier_account = EnvironmentVariables.objects.get_var("BKAPP_DEFAULT_SUPPLIER_ACCOUNT", 0)
    result = client.api.search_business(
        {
            "bk_supplier_account": bk_supplier_account,
            "condition": {"bk_data_status": {"$in": ["enable", "disabled", None]}, "bk_biz_id": bk_biz_id},
        },
        path_params={"bk_supplier_account": bk_supplier_account},
        headers={"X-Bk-Tenant-Id": tenant_id},
    )

    if result["result"]:
        data = result["data"]["info"]
    else:
        raise exceptions.APIError(system="cc", api="search_business", message=result["message"], result=result)

    if len(data) != 1:
        raise exceptions.APIError(system="cc", api="search_business", message=result["message"], result=result)

    return data[0]


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
