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

from builtins import object
from future.utils import with_metaclass


class InstanceInspect(with_metaclass(abc.ABCMeta, object)):
    @abc.abstractmethod
    def creator_type(self, instance):
        raise NotImplementedError()

    @abc.abstractmethod
    def creator_id(self, instance):
        raise NotImplementedError()

    @abc.abstractmethod
    def resource_id(self, instance):
        raise NotImplementedError()

    @abc.abstractmethod
    def resource_name(self, instance):
        raise NotImplementedError()

    @abc.abstractmethod
    def parent(self, instance):
        raise NotImplementedError()

    @abc.abstractmethod
    def scope_id(self, instance):
        raise NotImplementedError()


class DummyInspect(InstanceInspect):

    def creator_type(self, instance):
        return None

    def creator_id(self, instance):
        return None

    def resource_id(self, instance):
        return None

    def resource_name(self, instance):
        return None

    def parent(self, instance):
        return None

    def scope_id(self, instance):
        return None


class FieldInspect(InstanceInspect):
    def __init__(self, creator_type_f, creator_id_f, resource_id_f, resource_name_f, parent_f, scope_id_f):
        self.creator_type_f = creator_type_f
        self.creator_id_f = creator_id_f
        self.resource_id_f = resource_id_f
        self.resource_name_f = resource_name_f
        self.parent_f = parent_f
        self.scope_id_f = scope_id_f

    @classmethod
    def _getattr_if_field_is_not_none(cls, instance, f):
        return None if f is None else getattr(instance, f)

    def creator_type(self, instance):
        return self._getattr_if_field_is_not_none(instance, self.creator_type_f)

    def creator_id(self, instance):
        return self._getattr_if_field_is_not_none(instance, self.creator_id_f)

    def resource_id(self, instance):
        return self._getattr_if_field_is_not_none(instance, self.resource_id_f)

    def resource_name(self, instance):
        return self._getattr_if_field_is_not_none(instance, self.resource_name_f)

    def parent(self, instance):
        return self._getattr_if_field_is_not_none(instance, self.parent_f)

    def scope_id(self, instance):
        return self._getattr_if_field_is_not_none(instance, self.scope_id_f)


class FixedCreatorTypeFieldInspect(FieldInspect):
    def __init__(self, creator_type, creator_id_f, resource_id_f, resource_name_f, parent_f, scope_id_f):
        super(FixedCreatorTypeFieldInspect, self).__init__(creator_type_f='',
                                                           creator_id_f=creator_id_f,
                                                           resource_id_f=resource_id_f,
                                                           resource_name_f=resource_name_f,
                                                           parent_f=parent_f,
                                                           scope_id_f=scope_id_f)
        self._creator_type = creator_type

    def creator_type(self, instance):
        return self._creator_type
