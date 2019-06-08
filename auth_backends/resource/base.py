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


class ObjectResource(Resource):
    def __init__(self, resource_cls, *args, **kwargs):
        super(ObjectResource, self).__init__(*args, **kwargs)
        self.resource_cls = resource_cls
