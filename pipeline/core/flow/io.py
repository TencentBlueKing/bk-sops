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


class InputItem(object):
    def __init__(self, name, key, type, required=True, schema=None):
        self.name = name
        self.key = key
        self.type = type
        self.required = required
        self.schema = schema

    def as_dict(self):
        return {
            'name': self.name,
            'key': self.key,
            'type': self.type,
            'required': self.required,
            'schema': self.schema.as_dict() if self.schema else {}
        }


class OutputItem(object):
    def __init__(self, name, key, type, schema=None):
        self.name = name
        self.key = key
        self.type = type
        self.schema = schema

    def as_dict(self):
        return {
            'name': self.name,
            'key': self.key,
            'type': self.type,
            'schema': self.schema.as_dict() if self.schema else {}
        }


class ItemSchema(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, description, enum=None):
        self.type = self._type()
        self.description = description
        self.enum = enum or []

    def as_dict(self):
        return {
            'type': self.type,
            'description': self.description,
            'enum': self.enum
        }

    @abc.abstractmethod
    def _type(self):
        raise NotImplementedError()


class SimpleItemSchema(ItemSchema):
    __metaclass__ = abc.ABCMeta


class IntItemSchema(SimpleItemSchema):
    @classmethod
    def _type(cls):
        return 'int'


class StringItemSchema(SimpleItemSchema):
    @classmethod
    def _type(cls):
        return 'string'


class FloatItemSchema(SimpleItemSchema):
    @classmethod
    def _type(cls):
        return 'float'


class BooleanItemSchema(SimpleItemSchema):
    @classmethod
    def _type(cls):
        return 'boolean'


class ArrayItemSchema(ItemSchema):
    def __init__(self, item_schema, *args, **kwargs):
        self.item_schema = item_schema
        super(ArrayItemSchema, self).__init__(*args, **kwargs)

    def as_dict(self):
        base = super(ArrayItemSchema, self).as_dict()
        base['items'] = self.item_schema.as_dict()
        return base

    @classmethod
    def _type(cls):
        return 'array'


class ObjectItemSchema(ItemSchema):
    def __init__(self, property_schemas, *args, **kwargs):
        self.property_schemas = property_schemas
        super(ObjectItemSchema, self).__init__(*args, **kwargs)

    def as_dict(self):
        base = super(ObjectItemSchema, self).as_dict()
        properties = {prop: schema.as_dict() for prop, schema in self.property_schemas.items()}
        base['properties'] = properties
        return base

    @classmethod
    def _type(cls):
        return 'object'
