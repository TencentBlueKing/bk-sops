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

from abc import ABCMeta, abstractmethod

from builtins import object
from future.utils import with_metaclass


class AuthDelegation(with_metaclass(ABCMeta, object)):
    def __init__(self, delegate_resource, action_ids):
        self.delegate_resource = delegate_resource
        self.action_ids = action_ids

    @abstractmethod
    def delegate_instance(self, client_instance):
        raise NotImplementedError()


class RelateAuthDelegation(AuthDelegation):
    def __init__(self, delegate_instance_f=None, *args, **kwargs):
        super(RelateAuthDelegation, self).__init__(*args, **kwargs)
        self.delegate_instance_f = delegate_instance_f

    def delegate_instance(self, client_instance):
        return getattr(client_instance, self.delegate_instance_f, None)
