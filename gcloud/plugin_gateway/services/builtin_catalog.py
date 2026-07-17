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

from pipeline.component_framework.library import ComponentLibrary

from gcloud.plugin_gateway.constants import PLUGIN_SOURCE_BUILTIN, UNIFORM_API_WRAPPER_VERSION, encode_plugin_id


class BuiltinCatalogService:
    """Adapt built-in SOPS components to uniform_api v4 catalog fields."""

    @classmethod
    def list_plugins(cls):
        code_versions = {}
        code_components = {}
        for component_cls in ComponentLibrary.component_list():
            code = component_cls.code
            version = getattr(component_cls, "version", "legacy")
            code_versions.setdefault(code, []).append(version)
            code_components.setdefault(code, component_cls)

        plugins = []
        for code, versions in code_versions.items():
            component_cls = code_components[code]
            plugins.append(cls._build_meta(component_cls, code, versions))
        return sorted(plugins, key=lambda item: (item["name"], item["id"]))

    @classmethod
    def get_plugin_detail(cls, code, version=None):
        component_cls = cls._get_component_class(code, version)
        meta = cls._build_meta(component_cls, code, [getattr(component_cls, "version", "legacy")])
        service = component_cls.bound_service()
        meta["inputs"] = cls._convert_io(service.inputs_format())
        meta["outputs"] = cls._convert_io(service.outputs_format())
        return meta

    @staticmethod
    def _get_component_class(code, version=None):
        if version:
            return ComponentLibrary.get_component_class(code, version)
        return ComponentLibrary.get_component_class(code)

    @classmethod
    def _build_meta(cls, component_cls, code, versions):
        versions = sorted(set(versions))
        group_name = cls._stringify(getattr(component_cls, "group_name", "") or PLUGIN_SOURCE_BUILTIN)
        return {
            "id": encode_plugin_id(PLUGIN_SOURCE_BUILTIN, code),
            "plugin_source": PLUGIN_SOURCE_BUILTIN,
            "plugin_code": code,
            "name": cls._stringify(getattr(component_cls, "name", code)),
            "group": group_name,
            "category": group_name,
            "versions": versions,
            "default_version": getattr(component_cls, "version", versions[-1]),
            "latest_version": versions[-1],
            "wrapper_version": UNIFORM_API_WRAPPER_VERSION,
            "description": "",
        }

    @classmethod
    def _convert_io(cls, io_format):
        fields = []
        for item in io_format or []:
            schema = cls._get_item_value(item, "schema", None)
            fields.append(
                {
                    "key": cls._get_item_value(item, "key", ""),
                    "name": cls._get_item_value(item, "name", ""),
                    "type": cls._get_schema_type(schema),
                }
            )
        return fields

    @staticmethod
    def _get_item_value(item, key, default):
        if isinstance(item, dict):
            return item.get(key, default)
        return getattr(item, key, default)

    @staticmethod
    def _get_schema_type(schema):
        if not schema:
            return "string"
        if isinstance(schema, dict):
            return schema.get("type", "string")
        return getattr(schema, "type", "string")

    @staticmethod
    def _stringify(value):
        if value is None:
            return ""
        return str(value)
