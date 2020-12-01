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

from django.conf import settings

import env
from api.client import BKComponentClient

ITSM_API_ENTRY = env.BK_ITSM_API_ENTRY or "{}/{}".format(settings.BK_PAAS_INNER_HOST, "api/c/compapi/v2/itsm")


def _get_itsm_api(api_name):
    return "{}/{}/".format(ITSM_API_ENTRY, api_name)


class BKItsmClient(BKComponentClient):
    def create_ticket(self, creator, fields, fast_approval, meta):
        return self._request(
            method="post",
            url=_get_itsm_api("create_ticket"),
            data={
                "creator": creator,
                "fields": fields,
                "fast_approval": fast_approval,
                "meta": meta,
            },
        )
