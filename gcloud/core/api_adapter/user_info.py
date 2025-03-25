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

# get_client_by_user = settings.ESB_GET_CLIENT_BY_USER
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
    resp = client.api.list_users({"fields": "display_name,username,id", "no_page": True})

    if not resp["result"]:
        logger.error("usermanage API[list_users] return error: %s", resp)

    return {
        "code": resp.get("code"),
        "message": resp.get("message"),
        "data": resp.get("data"),
        "result": resp["result"],
    }
