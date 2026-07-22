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
from gcloud.plugin_gateway.services.builtin_form_schema import build_builtin_form_schema
from gcloud.plugin_gateway.services.form_schema import convert_component_io

INTERNAL_COMPONENT_CODES = {"remote_plugin", "subprocess_plugin"}


class BuiltinCatalogService:
    """Adapt built-in SOPS components to uniform_api v4 catalog fields."""

    @classmethod
    def list_plugins(cls):
        code_versions = {}
        code_components = {}
        for component_cls in ComponentLibrary.component_list():
            code = component_cls.code
            if code in INTERNAL_COMPONENT_CODES:
                continue
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
        input_format = service.inputs_format()
        meta["inputs"] = convert_component_io(input_format)
        meta["outputs"] = convert_component_io(service.outputs_format())
        form_schema = build_builtin_form_schema(code, input_format)
        if form_schema is not None:
            meta["form_schema"] = form_schema
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

    @staticmethod
    def _stringify(value):
        if value is None:
            return ""
        return str(value)
