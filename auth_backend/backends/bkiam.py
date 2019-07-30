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

from bkiam import bkiam_client

from auth_backend.backends.base import AuthBackend


class BkIAMBackend(AuthBackend):

    def __init__(self, client=None):
        self.client = client or bkiam_client

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

    def register_instance(self, resource, instance, scope_id=None):
        return self.client.register_resource(creator_type=resource.creator_type(instance),
                                             creator_id=resource.creator_id(instance),
                                             scope_type=resource.scope_type,
                                             scope_id=scope_id or resource.scope_id,
                                             resource_type=resource.rtype,
                                             resource_name=resource.resource_name(instance),
                                             resource_id=self._resource_id_for(resource, instance))

    def batch_register_instance(self, resource, instances, scope_id=None):
        if not instances:
            raise ValueError('can not batch register a empty instances list')

        iam_resources = []
        for instance in instances:
            iam_resources.append({
                'scope_type': resource.scope_type,
                'scope_id': scope_id or resource.scope_id,
                'resource_type': resource.rtype,
                'resource_id': self._resource_id_for(resource, instance),
                'resource_name': resource.resource_name(instance)
            })

        return self.client.batch_register_resource(creator_type=resource.creator_type(instances[0]),
                                                   creator_id=resource.creator_id(instances[0]),
                                                   resources=iam_resources)

    def update_instance(self, resource, instance, scope_id=None):
        return self.client.update_resource(scope_type=resource.scope_type,
                                           scope_id=scope_id or resource.scope_id,
                                           resource_type=resource.rtype,
                                           resource_id=self._resource_id_for(resource, instance),
                                           resource_name=resource.resource_name(instance))

    def delete_instance(self, resource, instance, scope_id=None):
        return self.client.delete_resource(scope_type=resource.scope_type,
                                           scope_id=scope_id or resource.scope_id,
                                           resource_type=resource.rtype,
                                           resource_id=self._resource_id_for(resource, instance))

    def batch_delete_instance(self, resource, instances, scope_id=None):
        iam_resources = []
        for instance in instances:
            iam_resources.append({
                'scope_type': resource.scope_type,
                'scope_id': scope_id or resource.scope_id,
                'resource_type': resource.rtype,
                'resource_id': self._resource_id_for(resource, instance),
                'resource_name': resource.resource_name(instance)
            })

        return self.client.batch_delete_resource(resources=iam_resources)

    def verify_perms(self, resource, principal_type, principal_id, action_ids, instance=None, scope_id=None):
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
                                                        scope_id=scope_id or resource.scope_id,
                                                        resources_actions=actions)

    def batch_verify_perms(self, resource, principal_type, principal_id, action_ids, instances=None, scope_id=None):
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
                                                        scope_id=scope_id or resource.scope_id,
                                                        resources_actions=actions)

    def verify_multiple_resource_perms(self, principal_type, principal_id, perms_tuples, scope_id=None):
        actions = []
        scope_type = None
        for perms_tuple in perms_tuples:
            resource = perms_tuple[0]
            instance = perms_tuple[2]
            scope_type = resource.scope_type
            scope_id = scope_id or resource.scope_id
            for action_id in perms_tuple[1]:
                action = {'action_id': action_id,
                          'resource_type': resource.rtype}

                if instance:
                    action['resource_id'] = self._resource_id_for(resource, instance)

                actions.append(action)

        return self.client.batch_verify_resources_perms(principal_type=principal_type,
                                                        principal_id=principal_id,
                                                        scope_type=scope_type,
                                                        scope_id=scope_id,
                                                        resources_actions=actions)

    def search_authorized_resources(self, resource, principal_type, principal_id, action_ids, scope_id=None):
        actions = [{'action_id': action_id, 'resource_type': resource.rtype} for action_id in action_ids]
        return self.client.search_authorized_resources(principal_type=principal_type,
                                                       principal_id=principal_id,
                                                       scope_type=resource.scope_type,
                                                       scope_id=scope_id or resource.scope_id,
                                                       resource_types_actions=actions,
                                                       resource_data_type='array',
                                                       is_exact_resource=True)

    def search_resources_perms_principals(self, resource, resources_actions, scope_id=None):
        actions = []
        for resource_action in resources_actions:
            action = {'action_id': resource_action['action_id'], 'resource_type': resource.rtype}
            instance = resource_action.get('instance')
            if instance:
                action['resource_id'] = self._resource_id_for(resource, instance)
        return self.client.search_resources_perms_principals(scope_type=resource.scope_type,
                                                             scope_id=scope_id or resource.scope_id,
                                                             resources_actions=actions)
