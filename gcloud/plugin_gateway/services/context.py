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

from copy import deepcopy
from urllib.parse import urlparse

from gcloud.plugin_gateway.exceptions import PluginGatewayContextResolveError, PluginGatewayPluginNotEnabledError


class PluginGatewayContextService:
    RUN_CONTEXT_KEYS = ("space_id", "task_id", "node_id", "task_name")

    @classmethod
    def build_trigger_payload(cls, source_config, plugin_id, payload):
        allow_list = source_config.plugin_allow_list or []
        if not allow_list:
            raise ValueError("plugin_allow_list is empty for source({})".format(source_config.source_key))
        if plugin_id not in allow_list:
            raise PluginGatewayPluginNotEnabledError(
                "plugin({}) is not enabled for source({})".format(plugin_id, source_config.source_key)
            )

        trigger_payload = deepcopy(payload)
        trigger_payload["context"] = deepcopy(payload.get("context") or {})
        if source_config.default_project_id and not trigger_payload.get("project_id"):
            trigger_payload["project_id"] = source_config.default_project_id
        return trigger_payload

    @classmethod
    def resolve_run_context(cls, source_config, context):
        context = context or {}
        scope_type = context.get("scope_type")
        scope_value = context.get("scope_value")
        project_id = cls._resolve_project_id(source_config, scope_type, scope_value)
        if project_id is None:
            raise PluginGatewayContextResolveError(
                "cannot resolve sops project from scope_type={} scope_value={}".format(scope_type, scope_value)
            )

        from gcloud.core.models import Project

        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            raise PluginGatewayContextResolveError("resolved project_id={} not found".format(project_id))

        resolved = {
            "project_id": project.id,
            "bk_biz_id": project.bk_biz_id,
            "operator": context.get("operator") or "",
            "scope_type": scope_type,
            "scope_value": scope_value,
        }
        for key in cls.RUN_CONTEXT_KEYS:
            resolved[key] = context.get(key)
        return resolved

    @staticmethod
    def _resolve_project_id(source_config, scope_type, scope_value):
        if scope_type in ("biz", "cmdb_biz") and scope_value:
            from gcloud.core.models import Project

            try:
                bk_biz_id = int(scope_value)
            except (TypeError, ValueError):
                bk_biz_id = None
            if bk_biz_id is not None:
                project = Project.objects.filter(bk_biz_id=bk_biz_id, from_cmdb=True).first()
                if project:
                    return project.id

        mapping = source_config.scope_project_map or {}
        if scope_type and scope_value:
            mapped_project_id = mapping.get("{}:{}".format(scope_type, scope_value))
            if mapped_project_id:
                return int(mapped_project_id)

        if source_config.default_project_id:
            return int(source_config.default_project_id)
        return None

    @classmethod
    def validate_callback_domain(cls, source_config, callback_url):
        allow_list = source_config.callback_domain_allow_list or []
        if not allow_list:
            raise ValueError("callback_domain_allow_list is empty for source({})".format(source_config.source_key))

        parsed = urlparse(callback_url)
        hostname = parsed.hostname
        if parsed.scheme not in {"http", "https"} or not hostname:
            raise ValueError("callback_url({}) is malformed".format(callback_url))
        if hostname not in allow_list:
            raise ValueError("callback_url host({}) is not allowed".format(hostname))
