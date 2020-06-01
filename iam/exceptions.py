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

import abc
import six

from .utils import gen_perms_apply_data


class AuthBaseException(Exception):
    pass


class AuthAPIError(AuthBaseException):
    pass


class AuthInvalidRequest(AuthBaseException):
    pass


class AuthInvalidParam(AuthBaseException):
    pass


class AuthInvalidOperation(AuthBaseException):
    pass


@six.add_metaclass(abc.ABCMeta)
class AuthFailedBaseException(AuthBaseException):
    @abc.abstractmethod
    def perms_apply_data(self):
        raise NotImplementedError()


class AuthFailedException(AuthFailedBaseException):
    def __init__(self, system, subject, action, resources):
        self.system = system
        self.subject = subject
        self.action = action
        self.resources = resources

    def perms_apply_data(self):
        return gen_perms_apply_data(
            self.system, self.subject, [{"action": self.action, "resources_list": [self.resources]}]
        )


class MultiAuthFailedException(AuthFailedBaseException):
    def __init__(self, system, subject, action, resources_list):
        self.system = system
        self.subject = subject
        self.action = action
        self.resources_list = resources_list

    def perms_apply_data(self):
        return gen_perms_apply_data(
            self.system, self.subject, [{"action": self.action, "resources_list": self.resources_list}]
        )


class RawAuthFailedException(AuthFailedBaseException):
    def __init__(self, permissions):
        self.permissions = permissions

    def perms_apply_data(self):
        return self.permissions
