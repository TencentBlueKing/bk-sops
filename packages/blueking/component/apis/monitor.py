# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from ..base import ComponentAPI


class CollectionsMonitor(object):
    """Collections of Monitor APIS"""

    def __init__(self, client):
        self.client = client

        self.query_strategy = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi/v2/monitor_v3/search_alarm_strategy/',
            description=u'查询策略'
        )
        self.create_shield = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi/v2/monitor_v3/add_shield/',
            description=u'创建告警屏蔽'
        )
        self.disable_shield = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi/v2/monitor_v3/disable_shield/',
            description=u'解除告警屏蔽'
        )
