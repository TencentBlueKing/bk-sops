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
__author__ = "蓝鲸智云"
__copyright__ = "Copyright (c) 2012-2018 Tencent. All Rights Reserved."

import logging

from gcloud.core import roles
from gcloud.conf import settings
from gcloud.core.models import EnvironmentVariables
from packages.bkapi.bk_cmdb.shortcuts import get_client_by_username

logger = logging.getLogger("root")


def get_business_group_members(tenant_id, bk_biz_id, groups):
    if not groups:
        return []

    client = get_client_by_username(settings.SYSTEM_USE_API_ACCOUNT, stage=settings.BK_APIGW_STAGE_NAME)

    group_fileds = [roles.CC_V2_ROLE_MAP.get(group) for group in groups]
    group_fileds = [group for group in group_fileds if group]

    supplier_account = EnvironmentVariables.objects.get_var("BKAPP_DEFAULT_SUPPLIER_ACCOUNT", 0)
    kwargs = {
        "bk_supplier_account": supplier_account,
        "condition": {"bk_biz_id": bk_biz_id},
        "fields": group_fileds,
    }
    result = client.api.search_business(
        kwargs,
        path_params={"bk_supplier_account": supplier_account},
        headers={"X-Bk-Tenant-Id": tenant_id},
    )

    if not result["result"]:
        logger.error("get_business_group_members search_business fail: args: {}, result: {}".format(kwargs, result))
        return []

    group_members = []
    info = result["data"]["info"][0]
    for field in group_fileds:
        members = info.get(field, "")
        if members:
            group_members.extend(members.split(","))

    return list(set(group_members))


def get_business_attrinfo(tenant_id, attrs: list) -> list:
    if not attrs:
        return []

    client = get_client_by_username(settings.SYSTEM_USE_API_ACCOUNT, stage=settings.BK_APIGW_STAGE_NAME)
    supplier_account = EnvironmentVariables.objects.get_var("BKAPP_DEFAULT_SUPPLIER_ACCOUNT", 0)
    kwargs = {
        "bk_supplier_account": supplier_account,
        "fields": [
            "bk_biz_id",
        ].extend(attrs),
    }
    result = client.api.search_business(
        kwargs,
        path_params={"bk_supplier_account": supplier_account},
        headers={"X-Bk-Tenant-Id": tenant_id},
    )
    if not result["result"]:
        logger.error("get_business_attrinfo search_business fail: args: {}, result: {}".format(kwargs, result))
        return []
    info = result["data"]["info"]
    return info
