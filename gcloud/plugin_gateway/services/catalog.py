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

from concurrent.futures import ThreadPoolExecutor
from threading import RLock
from urllib.parse import urlsplit

from cachetools import TTLCache, cached
from django.conf import settings
from django.urls import reverse

from gcloud.plugin_gateway.constants import (
    PLUGIN_GATEWAY_ALL_CATEGORY,
    PLUGIN_SOURCE_BUILTIN,
    PLUGIN_SOURCE_THIRD_PARTY,
    RUNNING_STATUS_VALUE,
    UNIFORM_API_WRAPPER_VERSION,
    decode_plugin_id,
)
from gcloud.plugin_gateway.exceptions import PluginGatewaySourceUnavailableError, PluginGatewayVersionNotFoundError
from gcloud.plugin_gateway.models import PluginGatewaySourceConfig
from gcloud.plugin_gateway.services.builtin_catalog import BuiltinCatalogService
from plugin_service.conf import PLUGIN_DISTRIBUTOR_NAME
from plugin_service.exceptions import PluginServiceException
from plugin_service.plugin_client import PluginServiceApiClient


class PluginGatewayCatalogService:
    POLLING_STATUS_KEY = "data.status"
    THIRD_PARTY_LIST_PAGE_SIZE = 200
    THIRD_PARTY_META_WORKERS = 8
    APIGW_BACKEND_PATH_PREFIX = "/apigw"

    @classmethod
    def get_categories(cls, plugin_source=None):
        categories = {}
        if not plugin_source or plugin_source == PLUGIN_SOURCE_BUILTIN:
            for plugin in BuiltinCatalogService.list_plugins():
                category = cls._stringify(plugin.get("category"))
                if category:
                    categories.setdefault(category, category)

        if not plugin_source or plugin_source == PLUGIN_SOURCE_THIRD_PARTY:
            tag_result = PluginServiceApiClient.get_plugin_tags_list()
            if tag_result.get("result") and isinstance(tag_result.get("data"), list):
                for tag in tag_result["data"]:
                    category = cls._stringify(tag.get("code_name"))
                    if category:
                        categories.setdefault(category, cls._stringify(tag.get("name")) or category)

        return [dict(PLUGIN_GATEWAY_ALL_CATEGORY)] + [
            {"id": category, "name": categories[category]} for category in sorted(categories)
        ]

    @classmethod
    def get_plugin_list(cls, request):
        meta = {"total": 0, "apis": []}
        plugin_source = request.GET.get("plugin_source")
        for item in cls._list_plugins(plugin_source=plugin_source):
            if plugin_source and item.get("plugin_source") != plugin_source:
                continue

            category = request.GET.get("category")
            if category and category != PLUGIN_GATEWAY_ALL_CATEGORY["id"] and item.get("category") != category:
                continue

            keyword = request.GET.get("key", "").strip().casefold()
            if keyword and not any(
                keyword in cls._stringify(item.get(field)).casefold() for field in ("id", "name", "plugin_code")
            ):
                continue

            item = dict(item)
            detail_url = cls._build_public_api_url(
                request,
                "apigw_plugin_gateway_detail",
                kwargs={"plugin_id": item["id"]},
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

        if plugin["plugin_source"] == PLUGIN_SOURCE_BUILTIN:
            detail_schema = BuiltinCatalogService.get_plugin_detail(plugin["plugin_code"], selected_version)
            inputs = detail_schema.get("inputs", [])
            outputs = detail_schema.get("outputs", [])
        else:
            detail_schema = cls._get_plugin_detail_schema(plugin["plugin_code"], selected_version)
            inputs = cls._convert_schema_fields(
                detail_schema.get("inputs"),
                required=detail_schema.get("inputs", {}).get("required", []),
            )
            outputs = cls._convert_schema_fields(detail_schema.get("outputs"), required=[])

        detail = {
            "id": plugin["id"],
            "name": plugin["name"],
            "plugin_source": plugin["plugin_source"],
            "plugin_code": plugin["plugin_code"],
            "plugin_version": selected_version,
            "version": UNIFORM_API_WRAPPER_VERSION,
            "wrapper_version": plugin["wrapper_version"],
            "description": plugin.get("description", ""),
            "methods": ["POST"],
            "inputs": inputs,
            "outputs": outputs,
            "polling": {
                "url": "",
                "task_tag_key": "open_plugin_run_id",
                "success_tag": {"key": cls.POLLING_STATUS_KEY, "value": "SUCCEEDED", "data_key": "data.outputs"},
                "fail_tag": {"key": cls.POLLING_STATUS_KEY, "value": "FAILED", "msg_key": "data.error_message"},
                "running_tag": {"key": cls.POLLING_STATUS_KEY, "value": RUNNING_STATUS_VALUE},
            },
        }
        detail["url"] = cls._build_public_api_url(request, "apigw_plugin_gateway_run_create")
        detail["polling"]["url"] = cls._build_public_api_url(request, "apigw_plugin_gateway_run_status")
        return detail

    @classmethod
    def _list_plugins(cls, plugin_source=None):
        if plugin_source == PLUGIN_SOURCE_BUILTIN:
            plugins = BuiltinCatalogService.list_plugins()
        elif plugin_source == PLUGIN_SOURCE_THIRD_PARTY:
            plugins = cls._list_third_party_plugins()
        else:
            plugins = BuiltinCatalogService.list_plugins() + cls._list_third_party_plugins()

        plugins = cls._filter_do_not_open_plugins(plugins)
        return sorted(plugins, key=lambda item: (item["name"], item["id"]))

    @classmethod
    def _list_third_party_plugins(cls):
        plugin_entries = cls._get_third_party_plugin_entries()
        if not plugin_entries:
            return []

        worker_count = min(cls.THIRD_PARTY_META_WORKERS, len(plugin_entries))
        with ThreadPoolExecutor(max_workers=worker_count) as executor:
            plugin_metas = executor.map(cls._get_plugin_meta, [plugin["code"] for plugin in plugin_entries])

        plugins = []
        for plugin, meta in zip(plugin_entries, plugin_metas):
            plugin_reference = cls._build_third_party_plugin_reference(plugin, meta)
            if plugin_reference:
                plugins.append(plugin_reference)

        return sorted(plugins, key=lambda item: (item["name"], item["id"]))

    @classmethod
    def _get_third_party_plugin_entries(cls, search_term=None):
        plugins = []
        offset = 0
        expected_total = None

        while True:
            request_kwargs = {
                "limit": cls.THIRD_PARTY_LIST_PAGE_SIZE,
                "offset": offset,
                "distributor_code_name": PLUGIN_DISTRIBUTOR_NAME,
            }
            if search_term:
                request_kwargs["search_term"] = search_term
            result = PluginServiceApiClient.get_plugin_list(**request_kwargs)
            if not result.get("result"):
                raise PluginGatewaySourceUnavailableError(result.get("message", "query plugin list failed"))

            data = result.get("data") or {}
            page_plugins = data.get("plugins")
            total = data.get("count")
            if not isinstance(page_plugins, list) or type(total) is not int or total < 0:
                raise PluginGatewaySourceUnavailableError("query plugin list returned invalid pagination data")
            if expected_total is None:
                expected_total = total
            elif total != expected_total:
                raise PluginGatewaySourceUnavailableError("plugin list count changed during pagination")

            plugins.extend(page_plugins)
            if len(plugins) == expected_total:
                break
            if len(plugins) > expected_total or len(page_plugins) != cls.THIRD_PARTY_LIST_PAGE_SIZE:
                raise PluginGatewaySourceUnavailableError("query plugin list returned incomplete pagination data")

            offset += cls.THIRD_PARTY_LIST_PAGE_SIZE

        return plugins

    @staticmethod
    def _build_third_party_plugin_reference(plugin, meta):
        if not meta:
            return None

        versions = meta.get("versions") or []
        if not versions:
            return None

        latest_version = versions[-1]
        category = meta.get("group") or meta.get("category") or meta.get("tag") or PLUGIN_SOURCE_THIRD_PARTY
        return {
            "id": plugin["code"],
            "name": plugin["name"],
            "plugin_source": PLUGIN_SOURCE_THIRD_PARTY,
            "plugin_code": plugin["code"],
            "group": category,
            "wrapper_version": UNIFORM_API_WRAPPER_VERSION,
            "default_version": latest_version,
            "latest_version": latest_version,
            "versions": versions,
            "category": category,
            "description": meta.get("description", ""),
        }

    @classmethod
    def get_plugin_reference(cls, plugin_id):
        plugin_source, plugin_code = decode_plugin_id(plugin_id)
        do_not_open = cls._do_not_open_plugin_ids()
        if plugin_id in do_not_open or plugin_code in do_not_open:
            return None

        if plugin_source == PLUGIN_SOURCE_BUILTIN:
            return next((item for item in BuiltinCatalogService.list_plugins() if item["id"] == plugin_id), None)
        if plugin_source != PLUGIN_SOURCE_THIRD_PARTY:
            return None

        plugin = next(
            (
                item
                for item in cls._get_third_party_plugin_entries(search_term=plugin_code)
                if item["code"] == plugin_code
            ),
            None,
        )
        if plugin is None:
            return None
        return cls._build_third_party_plugin_reference(plugin, cls._get_plugin_meta(plugin_code))

    @classmethod
    def _build_public_api_url(cls, request, view_name, kwargs=None):
        path = reverse(view_name, kwargs=kwargs)
        api_url_template = getattr(settings, "BK_API_URL_TMPL", "")
        stage_name = getattr(settings, "BK_APIGW_STAGE_NAME", "")
        if not api_url_template or not stage_name:
            return request.build_absolute_uri(path)

        api_name = getattr(settings, "BK_APIGW_NAME", "bk-sops")
        base_url = api_url_template.format(api_name=api_name, stage_name=stage_name).rstrip("/")
        if not urlsplit(base_url).path.rstrip("/").endswith("/{}".format(stage_name)):
            base_url = "{}/{}".format(base_url, stage_name)

        if path.startswith(cls.APIGW_BACKEND_PATH_PREFIX + "/"):
            path = path[len(cls.APIGW_BACKEND_PATH_PREFIX) :]
        return "{}{}".format(base_url, path)

    @classmethod
    def _filter_do_not_open_plugins(cls, plugins):
        do_not_open = cls._do_not_open_plugin_ids()
        if not do_not_open:
            return plugins

        filtered_plugins = []
        for plugin in plugins:
            _, plugin_code = decode_plugin_id(plugin["id"])
            if plugin["id"] in do_not_open or plugin_code in do_not_open:
                continue
            filtered_plugins.append(plugin)
        return filtered_plugins

    @staticmethod
    def _do_not_open_plugin_ids():
        plugin_ids = set()
        configs = PluginGatewaySourceConfig.objects.filter(is_enabled=True)
        for config in configs:
            plugin_ids.update(config.do_not_open_list or [])
        return plugin_ids

    @staticmethod
    @cached(cache=TTLCache(maxsize=64, ttl=60), key=lambda plugin_code: plugin_code, lock=RLock())
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
    @cached(
        cache=TTLCache(maxsize=128, ttl=60),
        key=lambda plugin_code, version: "{}:{}".format(plugin_code, version),
        lock=RLock(),
    )
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

    @staticmethod
    def _stringify(value):
        if value is None:
            return ""
        return str(value)
