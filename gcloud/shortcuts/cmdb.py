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
__author__ = "蓝鲸智云"
__copyright__ = "Copyright (c) 2012-2018 Tencent. All Rights Reserved."

import logging

from gcloud.core import roles
from gcloud.conf import settings

logger = logging.getLogger('root')
get_client_by_user = settings.ESB_GET_CLIENT_BY_USER


def get_business_group_members(bk_biz_id, groups):
    client = get_client_by_user(settings.SYSTEM_USE_API_ACCOUNT)

    group_fileds = [roles.CC_V2_ROLE_MAP.get(group) for group in groups]
    group_fileds = [group for group in group_fileds if group]

    kwargs = {
        'bk_supplier_account': 0,
        'condition': {
            'bk_biz_id': bk_biz_id
        },
        'fields': group_fileds
    }
    result = client.cc.search_business(kwargs)

    if not result['result']:
        logger.error('get_business_group_members search_business fail: args: {}, result: {}'.format(
            kwargs,
            result
        ))
        return []

    group_members = []
    info = result['data']['info'][0]
    for field in group_fileds:
        members = info.get(field, '').split(',')
        if members:
            group_members.extend(members)

    return list(set(group_members))
