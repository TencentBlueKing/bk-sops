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

from ..exceptions import InvalidOperation

resource_type_lib = {}


class Action(object):
    def __init__(self, id, name, is_instance_related):
        self.id = id
        self.name = name
        self.is_instance_related = is_instance_related


class Resource(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, rtype, name, scope_type, scope_id, actions, inspect, backend, parent=None, parent_getter=None):
        self.rtype = rtype
        self.name = name
        self.actions = actions
        self.scope_type = scope_type
        self.scope_id = scope_id
        self.inspect = inspect
        self.backend = backend
        self.parent = parent
        self.parent_getter = parent_getter
        self.actions_map = {act.id: act for act in actions}

        if rtype in resource_type_lib:
            raise KeyError('Resource with rtype: {rtype} already exist.'.format(rtype=rtype))

        resource_type_lib[rtype] = self

    def resource_id(self, instance):
        return self.inspect.resource_id(instance)

    def resource_name(self, instance):
        return self.inspect.resource_name(instance)

    def creator_type(self, instance):
        return self.inspect.creator_type(instance)

    def creator_id(self, instance):
        return self.inspect.creator_id(instance)

    def parent_instance(self, child):
        return self.inspect.parent(child)

    def is_instance_related_action(self, action_id):
        return self.actions_map[action_id].is_instance_related

    # api
    def register_instance(self, instance):
        return self.backend.register_instance(resource=self, instance=instance)

    def batch_register_instance(self, instances):
        return self.backend.batch_register_instance(resource=self, instances=instances)

    def update_instance(self, instance):
        return self.backend.update_instance(resource=self, instance=instance)

    def delete_instance(self, instance):
        return self.backend.delete_instance(resource=self, instance=instance)

    def batch_delete_instance(self, instances):
        return self.backend.batch_delete_instance(resource=self, instances=instances)

    def verify_perms(self, principal_type, principal_id, action_ids, instance=None):
        return self.backend.verify_perms(principal_type=principal_type,
                                         principal_id=principal_id,
                                         resource=self,
                                         instance=instance,
                                         action_ids=action_ids)

    def batch_verify_perms(self, principal_type, principal_id, action_ids, instances=None):
        return self.backend.batch_verify_perms(principal_type=principal_type,
                                               principal_id=principal_id,
                                               resource=self,
                                               instances=instances,
                                               action_ids=action_ids)


class NeverInitiateResource(Resource):
    def __init__(self, rtype, name, scope_type, scope_id, actions, backend):
        super(NeverInitiateResource, self).__init__(rtype=rtype,
                                                    name=name,
                                                    actions=actions,
                                                    scope_type=scope_type,
                                                    scope_id=scope_id,
                                                    backend=backend,
                                                    inspect=None)

    def resource_id(self, instance):
        raise InvalidOperation('can not perform instance related operation on NeverInitiateResource')

    def resource_name(self, instance):
        raise InvalidOperation('can not perform instance related operation on NeverInitiateResource')

    def creator_type(self, instance):
        raise InvalidOperation('can not perform instance related operation on NeverInitiateResource')

    def creator_id(self, instance):
        raise InvalidOperation('can not perform instance related operation on NeverInitiateResource')

    def parent_instance(self, child):
        raise InvalidOperation('can not perform instance related operation on NeverInitiateResource')

    def register_instance(self, instance):
        raise InvalidOperation('can not perform instance related operation on NeverInitiateResource')

    def batch_register_instance(self, instances):
        raise InvalidOperation('can not perform instance related operation on NeverInitiateResource')

    def update_instance(self, instance):
        raise InvalidOperation('can not perform instance related operation on NeverInitiateResource')

    def delete_instance(self, instance):
        raise InvalidOperation('can not perform instance related operation on NeverInitiateResource')

    def batch_delete_instance(self, instances):
        raise InvalidOperation('can not perform instance related operation on NeverInitiateResource')


class ObjectResource(Resource):
    def __init__(self, resource_cls, *args, **kwargs):
        super(ObjectResource, self).__init__(*args, **kwargs)
        self.resource_cls = resource_cls
