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

from cachetools import TTLCache, cached
from django.urls import reverse

from gcloud.plugin_gateway.constants import PLUGIN_GATEWAY_CATEGORIES, PLUGIN_SOURCE_THIRD_PARTY
from gcloud.plugin_gateway.exceptions import (
    PluginGatewaySourceUnavailableError,
    PluginGatewayVersionNotFoundError,
)
from plugin_service.exceptions import PluginServiceException
from plugin_service.plugin_client import PluginServiceApiClient


class PluginGatewayCatalogService:
    @classmethod
    def get_categories(cls):
        return copy.deepcopy(PLUGIN_GATEWAY_CATEGORIES)

    @classmethod
    def get_plugin_list(cls, request):
        meta = {"total": 0, "apis": []}
        for item in cls._list_plugins():
            item = copy.deepcopy(item)
            detail_url = request.build_absolute_uri(
                reverse("apigw_plugin_gateway_detail", kwargs={"plugin_id": item["id"]})
            )
            item["meta_url_template"] = "{}?version={{version}}".format(detail_url)
            meta["apis"].append(item)
        meta["total"] = len(meta["apis"])
        return meta

    @classmethod
    def get_plugin_detail(cls, request, plugin_id, version=None):
        plugin = cls.get_plugin_reference(plugin_id)
        if plugin is None:
            return None

        selected_version = version or plugin.get("default_version")
        if selected_version not in plugin.get("versions", []):
            raise PluginGatewayVersionNotFoundError(
                "plugin({}) version({}) is not available".format(plugin_id, selected_version)
            )

        detail_schema = cls._get_plugin_detail_schema(plugin["plugin_code"], selected_version)
        detail = {
            "id": plugin["id"],
            "name": plugin["name"],
            "plugin_source": plugin["plugin_source"],
            "plugin_code": plugin["plugin_code"],
            "plugin_version": selected_version,
            "wrapper_version": plugin["wrapper_version"],
            "description": plugin.get("description", ""),
            "methods": ["POST"],
            "inputs": cls._convert_schema_fields(
                detail_schema.get("inputs"),
                required=detail_schema.get("inputs", {}).get("required", []),
            ),
            "outputs": cls._convert_schema_fields(detail_schema.get("outputs"), required=[]),
            "polling": {
                "url": "",
                "task_tag_key": "open_plugin_run_id",
                "success_tag": {"key": "status", "value": "SUCCEEDED", "data_key": "data.outputs"},
                "fail_tag": {"key": "status", "value": "FAILED", "msg_key": "data.error_message"},
                "running_tag": {"key": "status", "value": "RUNNING"},
            },
        }
        detail["url"] = request.build_absolute_uri(reverse("apigw_plugin_gateway_run_create"))
        detail["polling"]["url"] = request.build_absolute_uri(reverse("apigw_plugin_gateway_run_status"))
        return detail

    @staticmethod
    @cached(cache=TTLCache(maxsize=1, ttl=60))
    def _list_plugins():
        result = PluginServiceApiClient.get_plugin_list(limit=200, offset=0)
        if not result.get("result"):
            raise PluginGatewaySourceUnavailableError(result.get("message", "query plugin list failed"))

        plugins = []
        for plugin in result.get("data", {}).get("plugins", []):
            meta = PluginGatewayCatalogService._get_plugin_meta(plugin["code"])
            if not meta:
                continue

            versions = meta.get("versions") or []
            if not versions:
                continue

            latest_version = versions[-1]
            plugins.append(
                {
                    "id": plugin["code"],
                    "name": plugin["name"],
                    "plugin_source": PLUGIN_SOURCE_THIRD_PARTY,
                    "plugin_code": plugin["code"],
                    "wrapper_version": meta.get("framework_version") or meta.get("runtime_version") or "",
                    "default_version": latest_version,
                    "latest_version": latest_version,
                    "versions": versions,
                    "category": PLUGIN_SOURCE_THIRD_PARTY,
                    "description": meta.get("description", ""),
                }
            )

        return sorted(plugins, key=lambda item: (item["name"], item["id"]))

    @classmethod
    def get_plugin_reference(cls, plugin_id):
        return next((item for item in cls._list_plugins() if item["id"] == plugin_id), None)

    @staticmethod
    @cached(cache=TTLCache(maxsize=64, ttl=60), key=lambda plugin_code: plugin_code)
    def _get_plugin_meta(plugin_code):
        try:
            plugin_client = PluginServiceApiClient(plugin_code)
        except PluginServiceException:
            return None

        result = plugin_client.get_meta()
        if not result.get("result"):
            return None
        return result.get("data", {})

    @staticmethod
    @cached(cache=TTLCache(maxsize=128, ttl=60), key=lambda plugin_code, version: "{}:{}".format(plugin_code, version))
    def _get_plugin_detail_schema(plugin_code, version):
        try:
            plugin_client = PluginServiceApiClient(plugin_code)
        except PluginServiceException as e:
            raise PluginGatewaySourceUnavailableError(str(e))

        detail_result = plugin_client.get_detail(version)
        if not detail_result.get("result"):
            raise PluginGatewaySourceUnavailableError(detail_result.get("message", "query plugin detail failed"))
        return detail_result.get("data", {})

    @staticmethod
    def _convert_schema_fields(schema, required):
        if not isinstance(schema, dict):
            return []

        required_fields = set(required or [])
        fields = []
        for key, field in (schema.get("properties") or {}).items():
            item = {
                "key": key,
                "name": field.get("title") or key,
                "type": field.get("type", "string"),
                "description": field.get("description", ""),
            }
            if key in required_fields:
                item["required"] = True
            if "default" in field:
                item["default"] = field["default"]
            fields.append(item)
        return fields
