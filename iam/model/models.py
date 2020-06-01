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

"""
first version model

for python3, the dataclass is a better solution, but currently we need to support both python2/python3

options:
- https://github.com/keleshev/schema
- https://github.com/Julian/jsonschema
"""


class SystemProviderConfig(object):
    def __init__(self, host, auth):
        self.host = host
        self.auth = auth


class System(object):
    def __init__(self, id, name, name_en, description, description_en, clients, provider_config):
        self.id = id
        self.name = name
        self.name_en = name_en
        self.description = description
        self.description_en = description_en
        self.clients = clients
        self.provider_config = provider_config


class ReferenceResourceType(object):
    def __init__(self, system_id, id):
        self.system_id = system_id
        self.id = id


class ResourceProviderConfig(object):
    def __init__(self, path):
        self.path = path


class ResourceType(object):
    def __init__(self, id, name, name_en, description, description_en, parents, provider_config, version):
        self.id = id
        self.name = name
        self.name_en = name_en
        self.description = description
        self.description_en = description_en

        self.parents = parents
        self.provider_config = provider_config
        self.version = version


class InstanceSelection(object):
    def __init__(self, name, name_en, resource_type_chain):
        self.name = name
        self.name_en = name_en
        # [ReferenceResourceType]
        self.resource_type_chain = resource_type_chain


class RelatedResourceType(object):
    def __init__(self, system_id, id, name_alias, name_alias_en, scope, selection_mode, instance_selection):
        self.system_id = system_id
        self.id = id
        self.name_alias = name_alias
        self.name_alias_en = name_alias_en
        self.scope = scope
        self.selection_mode = selection_mode
        self.instance_selection = instance_selection


class Action(object):
    def __init__(
        self, id, name, name_en, description, description_en, type, related_resource_types, related_actions, version
    ):
        self.id = id
        self.name = name
        self.name_en = name_en
        self.description = description
        self.description_en = description_en

        self.type = type
        self.related_resource_types = related_resource_types
        self.related_actions = related_actions
        self.version = version


class ActionTopology(object):
    def __init__(self, id, sub_actions, related_actions):
        self.id = id
        # [ActionTopology]
        self.sub_actions = sub_actions
        # [str, str]
        self.related_actions = related_actions
