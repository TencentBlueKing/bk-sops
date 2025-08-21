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

from gcloud.conf import settings
from gcloud.core.models import EnvironmentVariables
from packages.bkapi.bk_user.shortcuts import get_client_by_username

logger = logging.getLogger("root")


def get_user_info(username, tenant_id):
    """
    @summary: 获取用户信息，通过APIGW请求也会调用该函数，请确保开通了ESB白名单并通过get_client_by_user获取client
    @param username:
    @return:
    """
    client = get_client_by_username(username, stage=settings.BK_APIGW_STAGE_NAME)
    user_info = client.api.retrieve_user(path_params={"bk_username": username}, headers={"X-Bk-Tenant-Id": tenant_id})
    if "data" in user_info and isinstance(user_info["data"], dict):
        user_info["data"]["bk_supplier_account"] = EnvironmentVariables.objects.get_var(
            "BKAPP_DEFAULT_SUPPLIER_ACCOUNT", 0
        )
        user_info["data"]["bk_role"] = user_info["data"]["role"]
        user_info["data"]["bk_username"] = user_info["data"]["username"]
        user_info["data"]["phone"] = user_info["data"].get("telephone", "")
    return user_info


def get_all_users(request):
    client = get_client_by_username(request.user.username, stage=settings.BK_APIGW_STAGE_NAME)
    resp = client.api.list_user(
        {"fields": "display_name,username,id", "no_page": True},
        headers={"X-Bk-Tenant-Id": request.user.tenant_id},
    )

    if not resp["result"]:
        logger.error("usermanage API[list_users] return error: %s", resp)

    return {
        "code": resp.get("code"),
        "message": resp.get("message"),
        "data": resp.get("data"),
        "result": resp["result"],
    }


def get_bk_username_by_tenant(tenant_id):
    """
    @summary: 开启多租户: 获取对应租户bk_admin的bk_useranme ,不开启多租户直接返回 settings.SYSTEM_USE_API_ACCOUNT
    @param tenant_id: 租户ID
    @return:
    """

    if settings.ENABLE_MULTI_TENANT_MODE:
        # 查询环境变量表
        bk_username = EnvironmentVariables.objects.get_var(tenant_id)
        if bk_username:
            return bk_username

        # 调用接口查询
        client = get_client_by_username(username=settings.SYSTEM_USE_API_ACCOUNT, stage=settings.BK_APIGW_STAGE_NAME)
        result = client.api.batch_lookup_virtual_user(
            {"lookups": settings.SYSTEM_USE_API_ACCOUNT, "lookup_field": "login_name"},
            headers={"X-Bk-Tenant-Id": tenant_id},
        )

        if result["data"]:
            bk_username = result["data"][0]["bk_username"]
            # 写入环境变量表
            EnvironmentVariables.objects.create(key=tenant_id, value=bk_username)
            return bk_username

    return settings.SYSTEM_USE_API_ACCOUNT
