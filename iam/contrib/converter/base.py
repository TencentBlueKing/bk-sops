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


import six
import abc


@six.add_metaclass(abc.ABCMeta)
class Converter(object):
    def __init__(self, key_mapping=None):
        self.key_mapping = key_mapping

    @abc.abstractmethod
    def _eq(self, left, right):
        pass

    @abc.abstractmethod
    def _not_eq(self, left, right):
        pass

    @abc.abstractmethod
    def _in(self, left, right):
        pass

    @abc.abstractmethod
    def _not_in(self, left, right):
        pass

    @abc.abstractmethod
    def _contains(self, left, right):
        pass

    @abc.abstractmethod
    def _not_contains(self, left, right):
        pass

    @abc.abstractmethod
    def _starts_with(self, left, right):
        pass

    @abc.abstractmethod
    def _not_starts_with(self, left, right):
        pass

    @abc.abstractmethod
    def _ends_with(self, left, right):
        pass

    @abc.abstractmethod
    def _not_ends_with(self, left, right):
        pass

    @abc.abstractmethod
    def _lt(self, left, right):
        pass

    @abc.abstractmethod
    def _lte(self, left, right):
        pass

    @abc.abstractmethod
    def _gt(self, left, right):
        pass

    @abc.abstractmethod
    def _gte(self, left, right):
        pass

    @abc.abstractmethod
    def _any(self, left, right):
        pass

    @abc.abstractmethod
    def _and(self, content):
        pass

    @abc.abstractmethod
    def _or(self, content):
        pass

    @abc.abstractmethod
    def convert(self, data):
        pass
