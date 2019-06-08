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

from __future__ import absolute_import
from bkiam.client import BkIAMClient

from .base import AuthBackend
from ..resources import resource_type_lib


class BkIAMBackend(AuthBackend):

    def __init__(self, client=None):
        self.client = client or BkIAMClient()

    @staticmethod
    def __gen_complete_id(resource, instance, id_tree):
        if resource.parent:
            parent_resource = resource.parent
            BkIAMBackend.__gen_complete_id(parent_resource, resource.parent_instance(instance), id_tree)

        # bk_iam only accept str type id
        id_tree.append({'resource_type': resource.rtype, 'resource_id': str(resource.resource_id(instance))})

    @classmethod
    def _resource_id_for(cls, resource, instance):
        resource_id = []
        cls.__gen_complete_id(resource, instance, resource_id)
        return resource_id

    def register_instance(self, resource, instance):
        return self.client.register_resource(creator_type=resource.creator_type(instance),
                                             creator_id=resource.creator_id(instance),
                                             scope_type=resource.scope_type,
                                             scope_id=resource.scope_id,
                                             resource_type=resource.rtype,
                                             resource_name=resource.resource_name(instance),
                                             resource_id=self._resource_id_for(resource, instance))

    def batch_register_instance(self, resource, instances):
        if not instances:
            raise ValueError('can not batch register a empty instances list')

        iam_resources = []
        for instance in instances:
            iam_resources.append({
                'scope_type': resource.scope_type,
                'scope_id': resource.scope_id,
                'resource_type': resource.rtype,
                'resource_id': self._resource_id_for(resource, instance),
                'resource_name': resource.resource_name(instance)
            })

        return self.client.batch_register_resource(creator_type=resource.creator_type(instances[0]),
                                                   creator_id=resource.creator_id(instances[0]),
                                                   resources=iam_resources)

    def update_instance(self, resource, instance):
        return self.client.update_resource(scope_type=resource.scope_type,
                                           scope_id=resource.scope_id,
                                           resource_type=resource.rtype,
                                           resource_id=self._resource_id_for(resource, instance),
                                           resource_name=resource.resource_name(instance))

    def delete_instance(self, resource, instance):
        return self.client.delete_resource(scope_type=resource.scope_type,
                                           scope_id=resource.scope_id,
                                           resource_type=resource.rtype,
                                           resource_id=self._resource_id_for(resource, instance))

    def batch_delete_instance(self, resource, instances):
        iam_resources = []
        for instance in instances:
            iam_resources.append({
                'scope_type': resource.scope_type,
                'scope_id': resource.scope_id,
                'resource_type': resource.rtype,
                'resource_id': self._resource_id_for(resource, instance),
                'resource_name': resource.resource_name(instance)
            })

        return self.client.batch_delete_resource(resources=iam_resources)

    def verify_perms(self, principal_type, principal_id, resource, action_ids, instance=None):
        actions = []
        for action_id in action_ids:
            action = {'action_id': action_id,
                      'resource_type': resource.rtype}
            if resource.is_instance_related_action(action_id) and instance:
                action['resource_id'] = self._resource_id_for(resource, instance)

            actions.append(action)

        return self.client.batch_verify_resources_perms(principal_type=principal_type,
                                                        principal_id=principal_id,
                                                        scope_type=resource.scope_type,
                                                        scope_id=resource.scope_id,
                                                        resources_actions=actions)

    def batch_verify_perms(self, principal_type, principal_id, resource, action_ids, instances=None):
        actions = []
        for action_id in action_ids:
            action = {'action_id': action_id,
                      'resource_type': resource.rtype}
            if resource.is_instance_related_action(action_id) and instances:
                for instance in instances:
                    action['resource_id'] = self._resource_id_for(resource, instance)

            actions.append(action)

        return self.client.batch_verify_resources_perms(principal_type=principal_type,
                                                        principal_id=principal_id,
                                                        scope_type=resource.scope_type,
                                                        scope_id=resource.scope_id,
                                                        resources_actions=actions)

    def verify_multi_resource_perms(self, principal_type, principal_id, resource_actions):
        actions = []
        for resource_id, action_ids in resource_actions.items():
            for action_id in action_ids:
                actions.append({
                    'action_id': action_id,
                    'resource_type': resource_id
                })

        # use first resource type's scope info
        resource = resource_type_lib[list(resource_actions.keys())[0]]
        scope_type = resource.scope_type
        scope_id = resource.scope_id

        return self.client.batch_verify_resources_perms(principal_type=principal_type,
                                                        principal_id=principal_id,
                                                        scope_type=scope_type,
                                                        scope_id=scope_id,
                                                        resources_actions=actions)
