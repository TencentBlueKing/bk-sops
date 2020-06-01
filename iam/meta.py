# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

_SYSTEM = "system"
_RESOURCES = "resources"
_ACTIONS = "actions"

__meta_info__ = {_SYSTEM: {}, _RESOURCES: {}, _ACTIONS: {}}


def setup_system(system_id, system_name):
    __meta_info__[_SYSTEM].setdefault(system_id, {})["name"] = system_name


def get_system_name(system_id):
    return __meta_info__[_SYSTEM].get(system_id, {}).get("name")


def setup_resource(system_id, resource_id, resource_name):
    __meta_info__[_RESOURCES].setdefault(system_id, {}).setdefault(resource_id, {})["name"] = resource_name


def get_resource_name(system_id, resource_id):
    return __meta_info__[_RESOURCES].get(system_id, {}).get(resource_id, {}).get("name")


def setup_action(system_id, action_id, action_name):
    __meta_info__[_ACTIONS].setdefault(system_id, {}).setdefault(action_id, {})["name"] = action_name


def get_action_name(system_id, action_id):
    return __meta_info__[_ACTIONS].get(system_id, {}).get(action_id, {}).get("name")
