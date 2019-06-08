# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from . import exceptions


class Resource(object):
    def __init__(self, rtype, name, actions, parent=None, scope_type=None, scope_id=None, interface=None):
        self.rtype = rtype
        self.name = name
        self.actions = actions
        self.parent = parent
        self.scope_type = scope_type
        self.scope_id = scope_id
        self._interface = interface
        self.principal_type = 'user'

    def set_interface(self, interface):
        self._interface = interface

    def get_interface(self):
        if self._interface is None:
            raise exceptions.AuthInterfaceEmptyError('Auth interface is empty, please set interface first')
        return self._interface

    def action_id_to_name(self, action_id):
        for act in self.actions:
            if act['action_id'] == action_id:
                return act['action_name']
        return None

    def register_resource_type(self, interface):
        pass

    def register_resource_instance(self, interface):
        pass

    def verify_resource_perms(self, username, actions_id, resource_id=None):
        resource_action = {
            'action_id': actions_id,
            'resource_type': self.rtype,
        }
        if resource_id is not None:
            resource_action['resource_id'] = resource_id
        authorized_result = self.get_interface().batch_verify_resources_perms(
            principal_type=self.principal_type,
            principal_id=username,
            scope_type=self.scope_type,
            scope_id=self.scope_id,
            resources_actions=[resource_action]
        )
        return authorized_result

    def search_instances(self, username, actions):
        pass

    def search_authorized_resources(self, username, actions_id):
        resource_types_actions = [{
            'action_id': act,
            'resource_type': self.rtype
        } for act in actions_id]
        authorized_result = self.get_interface().search_authorized_resources(
            principal_type=self.principal_type,
            principal_id=username,
            scope_type=self.scope_type,
            scope_id=self.scope_id,
            resource_types_actions=resource_types_actions,
            resource_data_type='array',
            is_exact_resource=True
        )
        return authorized_result
