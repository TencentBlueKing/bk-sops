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

import copy

import ujson as json
from cachetools import TTLCache, cached
from django.urls import reverse

from gcloud.plugin_gateway.constants import PLUGIN_GATEWAY_CATEGORIES, PLUGIN_GATEWAY_FIXTURE_DIR
from gcloud.plugin_gateway.exceptions import PluginGatewayVersionNotFoundError


class PluginGatewayCatalogService:
    @classmethod
    def get_categories(cls):
        return copy.deepcopy(PLUGIN_GATEWAY_CATEGORIES)

    @classmethod
    def get_plugin_list(cls, request):
        meta = copy.deepcopy(cls._load_fixture("list_meta"))
        for item in meta.get("apis", []):
            detail_url = request.build_absolute_uri(
                reverse("apigw_plugin_gateway_detail", kwargs={"plugin_id": item["id"]})
            )
            item["meta_url_template"] = "{}?version={{version}}".format(detail_url)
        return meta

    @classmethod
    def get_plugin_detail(cls, request, plugin_id, version=None):
        detail_meta = copy.deepcopy(cls._load_fixture("detail_meta"))
        detail = next((item for item in detail_meta.get("apis", []) if item["id"] == plugin_id), None)
        if detail is None:
            return None

        selected_version = version or detail.get("default_version")
        if selected_version not in detail.get("versions", []):
            raise PluginGatewayVersionNotFoundError(
                "plugin({}) version({}) is not available".format(plugin_id, selected_version)
            )

        detail["plugin_version"] = selected_version
        detail["url"] = request.build_absolute_uri(reverse("apigw_plugin_gateway_run_create"))
        detail["polling"]["url"] = request.build_absolute_uri(reverse("apigw_plugin_gateway_run_status"))
        return detail

    @staticmethod
    @cached(cache=TTLCache(maxsize=16, ttl=60), key=lambda name: name)
    def _load_fixture(name):
        # NOTE: 该缓存为进程级，多 worker 部署下每个 worker 独立缓存；ttl=60s 内
        # 不同 worker 可能短暂返回不同内容。fixture 当前随代码发布，可接受；
        # 若后续接入动态 fixture（例如从注册中心拉取），需要改造为 Redis 缓存。
        fixture_path = PLUGIN_GATEWAY_FIXTURE_DIR / "{}.json".format(name)
        with fixture_path.open(encoding="utf-8") as fixture:
            return json.load(fixture)
