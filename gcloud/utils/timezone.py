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

from packages.bkapi.bk_login.shortcuts import get_client_by_request

logger = logging.getLogger("root")

NOT_FOUND = object()


def get_user_timezone(request, use_cache=True):
    user_time_zone_cache_key = f"{request.user.username}_time_zone"
    if use_cache:
        time_zone_cache = cache.get(user_time_zone_cache_key, default=NOT_FOUND)
        if time_zone_cache is not NOT_FOUND:
            # use cache
            return time_zone_cache

    time_zone = None
    # get time_zone of user
    try:
        client = get_client_by_request(request)
        user_info = client.api.get_bk_token_userinfo(
            {"bk_token": request.COOKIES.get("bk_token")}, headers={"X-Bk-Tenant-Id": request.user.tenant_id}
        )

        time_zone = user_info.get("data", {}).get("time_zone", "")
    except Exception as e:
        logger.error("get time_zone error: {}".format(e))

    cache.set(user_time_zone_cache_key, time_zone, 15 * 60)
    return time_zone
