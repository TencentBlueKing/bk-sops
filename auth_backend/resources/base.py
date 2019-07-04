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

import abc

from auth_backend import exceptions
from auth_backend.backends import get_backend_from_config

resource_type_lib = {}


class Action(object):
    def __init__(self, id, name, is_instance_related):
        self.id = id
        self.name = name
        self.is_instance_related = is_instance_related

    def dict(self):
        return {'id': self.id, 'name': self.name}


class ActionCollection(object):
    def __init__(self, actions):
        for action in actions:
            setattr(self, action.id, action)
        self._actions = actions

    def __iter__(self):
        return iter(self._actions)


class Resource(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, rtype, name, scope_type, scope_id, scope_name, actions, inspect,
                 parent=None, parent_getter=None, operations=None, backend=None):
        self.rtype = rtype
        self.name = name
        self.actions = ActionCollection(actions)
        self.scope_type = scope_type
        self.scope_id = scope_id
        self.scope_name = scope_name
        self.inspect = inspect
        self.backend = backend or get_backend_from_config()
        self.parent = parent
        self.parent_getter = parent_getter
        self.actions_map = {act.id: act for act in actions}

        if rtype in resource_type_lib:
            raise exceptions.AuthKeyError('Resource with rtype: {rtype} already exist.'.format(rtype=rtype))

        if operations is None:
            operations = []
        for operation in operations:
            operation['actions'] = [getattr(self.actions, act).dict() for act in operation['actions_id']]
        self.operations = operations

        resource_type_lib[rtype] = self

    def base_info(self):
        return {
            'system_id': self.backend.client.system_id,
            'system_name': self.backend.client.system_name,
            'scope_type': self.scope_type,
            'scope_id': self.scope_id,
            'scope_name': self.scope_name,
            'resource': {
                'resource_type': self.rtype,
                'resource_type_name': self.name,
            }
        }

    def snapshot(self):
        return {
            'resource_type': self.rtype,
            'resource_type_name': self.name,
            'parent_resource_type': self.parent.rtype if self.parent else '',
            'actions': [{
                'action_id': action.id,
                'action_name': action.name,
                'is_related_resource': action.is_instance_related
            } for action in self.actions]
        }

    def clean_instances(self, instances):
        return instances

    def resource_id(self, instance):
        return self.inspect.resource_id(self.clean_instances(instance))

    def resource_name(self, instance):
        return self.inspect.resource_name(self.clean_instances(instance))

    def creator_type(self, instance):
        return self.inspect.creator_type(self.clean_instances(instance))

    def creator_id(self, instance):
        return self.inspect.creator_id(self.clean_instances(instance))

    def parent_instance(self, child):
        return self.inspect.parent(child)

    def is_instance_related_action(self, action_id):
        return self.actions_map[action_id].is_instance_related

    def register_instance(self, instance):
        return self.backend.register_instance(resource=self, instance=self.clean_instances(instance))

    def batch_register_instance(self, instances):
        return self.backend.batch_register_instance(resource=self, instances=self.clean_instances(instances))

    def update_instance(self, instance):
        return self.backend.update_instance(resource=self, instance=self.clean_instances(instance))

    def delete_instance(self, instance):
        return self.backend.delete_instance(resource=self, instance=self.clean_instances(instance))

    def batch_delete_instance(self, instances):
        return self.backend.batch_delete_instance(resource=self, instances=self.clean_instances(instances))

    def verify_perms(self, principal_type, principal_id, action_ids, instance=None):
        return self.backend.verify_perms(principal_type=principal_type,
                                         principal_id=principal_id,
                                         resource=self,
                                         instance=self.clean_instances(instance),
                                         action_ids=action_ids)

    def batch_verify_perms(self, principal_type, principal_id, action_ids, instances=None):
        return self.backend.batch_verify_perms(principal_type=principal_type,
                                               principal_id=principal_id,
                                               resource=self,
                                               instances=self.clean_instances(instances),
                                               action_ids=action_ids)

    def search_resources_perms_principals(self, resources_actions):
        return self.backend.search_resources_perms_principals(principal_type=self.scope_type,
                                                              scope_id=self.scope_id,
                                                              resources_actions=resources_actions)


class NeverInitiateResource(Resource):
    def __init__(self, rtype, name, scope_type, scope_id, scope_name, actions, backend):
        super(NeverInitiateResource, self).__init__(rtype=rtype,
                                                    name=name,
                                                    actions=actions,
                                                    scope_type=scope_type,
                                                    scope_id=scope_id,
                                                    scope_name=scope_name,
                                                    backend=backend,
                                                    inspect=None)

    def resource_id(self, instance):
        raise exceptions.AuthInvalidOperationError(
            'can not perform instance related operation on NeverInitiateResource')

    def resource_name(self, instance):
        raise exceptions.AuthInvalidOperationError(
            'can not perform instance related operation on NeverInitiateResource')

    def creator_type(self, instance):
        raise exceptions.AuthInvalidOperationError(
            'can not perform instance related operation on NeverInitiateResource')

    def creator_id(self, instance):
        raise exceptions.AuthInvalidOperationError(
            'can not perform instance related operation on NeverInitiateResource')

    def parent_instance(self, child):
        raise exceptions.AuthInvalidOperationError(
            'can not perform instance related operation on NeverInitiateResource')

    def register_instance(self, instance):
        raise exceptions.AuthInvalidOperationError(
            'can not perform instance related operation on NeverInitiateResource')

    def batch_register_instance(self, instances):
        raise exceptions.AuthInvalidOperationError(
            'can not perform instance related operation on NeverInitiateResource')

    def update_instance(self, instance):
        raise exceptions.AuthInvalidOperationError(
            'can not perform instance related operation on NeverInitiateResource')

    def delete_instance(self, instance):
        raise exceptions.AuthInvalidOperationError(
            'can not perform instance related operation on NeverInitiateResource')

    def batch_delete_instance(self, instances):
        raise exceptions.AuthInvalidOperationError(
            'can not perform instance related operation on NeverInitiateResource')


class ObjectResource(Resource):
    def __init__(self, resource_cls, *args, **kwargs):
        super(ObjectResource, self).__init__(*args, **kwargs)
        self.resource_cls = resource_cls
