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


class DictObject(object):
    def __init__(self, obj):
        self.obj = obj
        self.is_dict = isinstance(obj, dict)

    def __getattr__(self, key):
        if self.is_dict:
            return self.obj.get(key)
        else:
            if hasattr(self.obj, key):
                return getattr(self.obj, key)
            return None

    def __setattr__(self, key, value):
        if key in ("obj", "is_dict"):
            super(DictObject, self).__setattr__(key, value)
            return

        raise AttributeError("read only object")


class ObjectSet(object):
    def __init__(self):
        self._data = {}

    def add_object(self, _type, obj):
        self._data[_type] = obj

    def get_object(self, _type):
        return self._data.get(_type)

    def has_object(self, _type):
        return _type in self._data

    def del_object(self, _type):
        if _type in self._data:
            del self._data[_type]

    def get(self, key):
        parts = key.split(".")
        if len(parts) != 2:
            return None

        _type, attribute_name = parts

        has_object = self.has_object(_type)
        if not has_object:
            return None

        obj = self.get_object(_type)
        if isinstance(obj, dict):
            return obj[attribute_name]

        return getattr(obj, attribute_name)
