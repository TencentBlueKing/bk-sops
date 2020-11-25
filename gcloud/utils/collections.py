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

gcloud.utils.collections
An extension of built-in collections module.
"""

from __future__ import absolute_import

from collections import *  # noqa


class ConstantDict(dict):
    """ConstantDict is a subclass of :class:`dict`, implementing __setitem__
    method to avoid item assignment::

    >>> d = ConstantDict({'key': 'value'})
    >>> d['key'] = 'value'
    Traceback (most recent call last):
        ...
    TypeError: 'ConstantDict' object does not support item assignment
    """

    def __setitem__(self, key, value):
        raise TypeError("'%s' object does not support item assignment"
                        % self.__class__.__name__)
