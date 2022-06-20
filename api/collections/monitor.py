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

from django.conf import settings

import env
from api.client import BKComponentClient


MONITOR_API_ENTRY = env.BK_MONITOR_API_ENTRY or "{}/{}".format(
    settings.BK_PAAS_ESB_HOST, "api/c/compapi/v2/monitor_v3"
)


def _get_monitor_api(api_name):
    return "{}/{}/".format(MONITOR_API_ENTRY, api_name)


class BKMonitorClient(BKComponentClient):
    def search_alarm_strategy(self, bk_biz_id):
        return self._request(
            method="post", url=_get_monitor_api("search_alarm_strategy"), data={"bk_biz_id": bk_biz_id}
        )

    def add_shield(
        self,
        bk_biz_id,
        category,
        description,
        begin_time,
        end_time,
        cycle_config,
        shield_notice,
        dimension_config,
        notice_config=None,
    ):
        return self._request(
            method="post",
            url=_get_monitor_api("add_shield"),
            data={
                "bk_biz_id": bk_biz_id,
                "category": category,
                "description": description,
                "begin_time": begin_time,
                "end_time": end_time,
                "cycle_config": cycle_config,
                "shield_notice": shield_notice,
                "dimension_config": dimension_config,
                "notice_config": notice_config or {},
            },
        )

    def disable_shield(self, id):
        return self._request(method="post", url=_get_monitor_api("disable_shield"), data={"id": id})
