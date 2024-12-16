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

import requests

from gcloud.conf import settings


class MarketAPIClient:
    def __init__(self):
        self.base_url = settings.TEMPLATE_MARKET_API_URL

    def _get_url(self, endpoint):
        return f"{self.base_url}{endpoint}"

    def get_service_category(self):
        url = self._get_url("/category/get_service_category/")
        response = requests.get(url)
        return response.json()

    def get_scene_label(self):
        url = self._get_url("/sre_property/scene_label/")
        response = requests.get(url)
        return response.json()

    def get_risk_level(self, request):
        url = self._get_url("/sre_scene/risk_level/")
        response = requests.get(url)
        return response.json()

    def get_template_scene_detail(self, market_record_id):
        url = self._get_url(f"/sre_scene/flow_template_scene/{market_record_id}/")
        response = requests.get(url)
        return response.json()

    def get_template_scene_list(self):
        url = self._get_url("/sre_scene/flow_template_scene/?is_all=true")
        response = requests.get(url)
        return response.json()

    def create_template_scene(self, data):
        url = self._get_url("/sre_scene/flow_template_scene/")
        response = requests.post(url, json=data)
        return response.json()

    def patch_template_scene(self, data, market_record_id):
        url = self._get_url(f"/sre_scene/flow_template_scene/{market_record_id}/")
        response = requests.patch(url, json=data)
        return response.json()
