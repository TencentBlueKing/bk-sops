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


class PluginGatewayContextService:
    @classmethod
    def build_trigger_payload(cls, source_config, plugin_id, payload):
        allow_list = source_config.plugin_allow_list or []
        if not allow_list:
            raise ValueError("plugin_allow_list is empty for source({})".format(source_config.source_key))
        if plugin_id not in allow_list:
            raise ValueError("plugin({}) is not enabled for source({})".format(plugin_id, source_config.source_key))

        trigger_payload = deepcopy(payload)
        if source_config.default_project_id and not trigger_payload.get("project_id"):
            trigger_payload["project_id"] = source_config.default_project_id
        return trigger_payload

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
