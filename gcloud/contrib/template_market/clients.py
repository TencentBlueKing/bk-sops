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
import json
import requests

from gcloud.conf import settings


class MarketAPIClient:
    def __init__(self, username):
        self.base_url = settings.TEMPLATE_MARKET_API_URL
        self.headers = {
            "X-Bkapi-Authorization": json.dumps(
                {"bk_app_code": settings.APP_CODE, "bk_app_secret": settings.SECRET_KEY, "bk_username": username}
            ),
            "Content-Type": "application/json",
        }

    def _get_url(self, endpoint):
        return f"{self.base_url}{endpoint}"

    def _make_request(self, method, endpoint, **kwargs):
        url = self._get_url(endpoint)
        response = requests.request(method, url, headers=self.headers, json=kwargs.get("data"))
        return response.json()

    def get_service_category(self):
        return self._make_request("GET", "/category/get_service_category/")

    def get_scene_label(self):
        return self._make_request("GET", "/sre_property/scene_label/")

    def get_risk_level(self):
        return self._make_request("GET", "/sre_scene/risk_level/")

    def get_template_scene_detail(self, market_record_id):
        return self._make_request("GET", f"/sre_scene/flow_template_scene/{market_record_id}/")

    def get_template_scene_list(self):
        return self._make_request("GET", "/sre_scene/flow_template_scene/?is_all=true")

    def create_template_scene(self, data):
        return self._make_request("POST", "/sre_scene/flow_template_scene/", data=data)

    def patch_template_scene(self, data, market_record_id):
        return self._make_request("PATCH", f"/sre_scene/flow_template_scene/{market_record_id}/", data=data)
