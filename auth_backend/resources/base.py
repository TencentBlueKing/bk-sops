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

from __future__ import absolute_import, unicode_literals

import abc
import copy

from builtins import object
from future.utils import with_metaclass

from auth_backend import conf, exceptions
from auth_backend.backends import get_backend_from_config
from auth_backend.resources.inspect import DummyInspect
from auth_backend.resources.interfaces import InstanceIterableResource

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


class Resource(with_metaclass(abc.ABCMeta, object)):
    def __init__(
        self,
        rtype,
        name,
        scope_type,
        scope_name,
        actions,
        inspect,
        scope_id=None,
        parent=None,
        operations=None,
        backend=None,
        properties=None
    ):
        self.rtype = rtype
        self.name = name
        self.actions = ActionCollection(actions)
        self.scope_type = scope_type
        self.scope_id = scope_id
        self.scope_name = scope_name
        self.inspect = inspect
        self.backend = backend or get_backend_from_config()
        self.parent = parent
        self.actions_map = {act.id: act for act in actions}
        self.properties = properties

        if rtype in resource_type_lib:
            raise exceptions.AuthKeyError('Resource with rtype: {rtype} already exist.'.format(rtype=rtype))

        _operations = [] if operations is None else copy.deepcopy(operations)
        for operation in _operations:
            operation['actions'] = [getattr(self.actions, act).dict() for act in operation['actions_id']]
        self.operations = _operations

        resource_type_lib[rtype] = self

    def __repr__(self):
        return '<Resource> {rtype}'.format(rtype=self.rtype)

    def base_info(self):
        return {
            'system_id': conf.SYSTEM_ID,
            'system_name': conf.SYSTEM_NAME,
            'scope_type': self.scope_type,
            'scope_type_name': conf.SCOPE_TYPE_NAMES[self.scope_type],
            'scope_id': self.scope_id,
            'scope_name': self.scope_name,
            'resource': {
                'resource_type': self.rtype,
                'resource_type_name': self.name,
            }
        }

    def snapshot(self):
        snapshot = {
            'resource_type': self.rtype,
            'resource_type_name': self.name,
            'parent_resource_type': self.parent.rtype if self.parent else '',
            'actions': [{
                'action_id': action.id,
                'action_name': action.name,
                'is_related_resource': action.is_instance_related
            } for action in self.actions],
        }
        if self.properties:
            snapshot['properties'] = self.properties

        return snapshot

    def clean_instances(self, instances):
        t = type(instances).__name__
        clean_method = getattr(self, 'clean_{type}_instances'.format(type=t), None)

        if clean_method:
            return clean_method(instances)

        return instances

    def real_scope_id(self, instance, candidate):
        scope_id = self.scope_id
        if scope_id:
            return scope_id

        scope_id = self.inspect.scope_id(instance) if instance else None
        if scope_id:
            return scope_id

        return candidate

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

    def resource_properties(self, instance):
        return self.inspect.properties(instance)

    def is_instance_related_action(self, action_id):
        return self.actions_map[action_id].is_instance_related

    def register_instance(self, instance, scope_id=None):
        clean_instance = self.clean_instances(instance)
        return self.backend.register_instance(
            resource=self,
            instance=clean_instance,
            scope_id=self.real_scope_id(clean_instance, scope_id)
        )

    def batch_register_instance(self, instances, scope_id=None):
        clean_instances = self.clean_instances(instances)
        if clean_instances:
            scope_id = self.real_scope_id(clean_instances[0], scope_id)
        return self.backend.batch_register_instance(resource=self,
                                                    instances=clean_instances,
                                                    scope_id=scope_id)

    def update_instance(self, instance, scope_id=None):
        clean_instance = self.clean_instances(instance)
        return self.backend.update_instance(resource=self,
                                            instance=clean_instance,
                                            scope_id=self.real_scope_id(clean_instance, scope_id))

    def delete_instance(self, instance, scope_id=None):
        clean_instance = self.clean_instances(instance)
        return self.backend.delete_instance(resource=self,
                                            instance=clean_instance,
                                            scope_id=self.real_scope_id(clean_instance, scope_id))

    def batch_delete_instance(self, instances, scope_id=None):
        clean_instances = self.clean_instances(instances)
        if clean_instances:
            scope_id = self.real_scope_id(clean_instances[0], scope_id)
        return self.backend.batch_delete_instance(
            resource=self,
            instances=clean_instances,
            scope_id=scope_id
        )

    def verify_perms(self, principal_type, principal_id, action_ids, instance=None, scope_id=None):
        clean_instances = self.clean_instances(instance)
        return self.backend.verify_perms(
            principal_type=principal_type,
            principal_id=principal_id,
            resource=self,
            instance=clean_instances,
            action_ids=action_ids,
            scope_id=self.real_scope_id(clean_instances, scope_id)
        )

    def batch_verify_perms(self, principal_type, principal_id, action_ids, instances=None, scope_id=None):
        clean_instances = self.clean_instances(instances)
        if clean_instances:
            scope_id = self.real_scope_id(clean_instances[0], scope_id)
        return self.backend.batch_verify_perms(
            principal_type=principal_type,
            principal_id=principal_id,
            resource=self,
            instances=clean_instances,
            action_ids=action_ids,
            scope_id=scope_id
        )

    def search_resources_perms_principals(self, resources_actions, scope_id=None):
        return self.backend.search_resources_perms_principals(
            resource=self,
            scope_id=self.real_scope_id(None, scope_id),
            resources_actions=resources_actions
        )


class NeverInitiateResource(Resource):
    def __init__(self, rtype, name, scope_type, scope_name, actions, scope_id=None, operations=None, backend=None):
        super(NeverInitiateResource, self).__init__(rtype=rtype,
                                                    name=name,
                                                    actions=actions,
                                                    scope_type=scope_type,
                                                    scope_id=scope_id,
                                                    scope_name=scope_name,
                                                    backend=backend,
                                                    operations=operations,
                                                    inspect=DummyInspect())

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


class ObjectResource(Resource, InstanceIterableResource):
    def __init__(self, resource_cls, *args, **kwargs):
        super(ObjectResource, self).__init__(*args, **kwargs)
        self.resource_cls = resource_cls

    def clean_instances(self, instances):
        if isinstance(instances, self.resource_cls):
            return instances

        return super(ObjectResource, self).clean_instances(instances)
