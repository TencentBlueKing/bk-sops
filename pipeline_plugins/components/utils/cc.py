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

from packages.bkapi.bk_cmdb.shortcuts import get_client_by_username

from gcloud.exceptions import APIError
from gcloud.conf import settings


def has_biz_set(tenant_id, bk_scope_id: int):
    """
    判断是否存在 id 为 bk_scope_id 的业务集

    :param tenant_id: 租户 ID
    :param bk_scope_id: 业务集 ID
    """
    client = get_client_by_username(settings.SYSTEM_USE_API_ACCOUNT, stage=settings.BK_APIGW_STAGE_NAME)
    resp = client.api.list_business_set(
        {
            "bk_biz_set_filter": {
                "condition": "AND",
                "rules": [{"field": "bk_biz_set_id", "operator": "equal", "value": bk_scope_id}],
            }
        },
        headers={"X-Bk-Tenant-Id": tenant_id},
    )
    if not resp["result"]:
        raise APIError(system="cc", api="list_business_set", message=resp.get("message"), result=resp)
    return resp["data"]["info"] is not None and len(resp["data"]["info"]) > 0
