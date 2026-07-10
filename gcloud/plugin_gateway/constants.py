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

from pathlib import Path

PLUGIN_SOURCE_BUILTIN = "builtin"
PLUGIN_SOURCE_THIRD_PARTY = "third_party"
PLUGIN_ID_SEP = "__"
RUNNING_STATUS_VALUE = "RUNNING"
MAX_SCHEDULE_TIMES = 1000

PLUGIN_GATEWAY_CATEGORIES = [
    {"id": PLUGIN_SOURCE_BUILTIN, "name": "标准运维内置插件"},
    {"id": PLUGIN_SOURCE_THIRD_PARTY, "name": "标准运维第三方插件"},
]

PLUGIN_GATEWAY_FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures" / "uniform_api_v4"


def encode_plugin_id(plugin_source, plugin_code):
    if plugin_source == PLUGIN_SOURCE_THIRD_PARTY:
        return plugin_code
    return "{}{}{}".format(plugin_source, PLUGIN_ID_SEP, plugin_code)


def decode_plugin_id(plugin_id):
    if PLUGIN_ID_SEP in plugin_id:
        source, _, code = plugin_id.partition(PLUGIN_ID_SEP)
        return source, code
    return PLUGIN_SOURCE_THIRD_PARTY, plugin_id


def poll_countdown(schedule_times):
    return 10 if schedule_times < 30 else min((schedule_times - 25) ** 2, 600)
