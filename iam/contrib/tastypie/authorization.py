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
import logging

from tastypie.authorization import Authorization, ReadOnlyAuthorization, Unauthorized
from tastypie.exceptions import ImmediateHttpResponse

from iam import Request, Action
from iam.exceptions import AuthFailedException
from iam.contrib.django.response import IAMAuthFailedResponse

logger = logging.getLogger("iam")


@six.add_metaclass(abc.ABCMeta)
class IAMAuthorizationHelper(object):
    def __init__(
        self, system, create_action, read_action, update_action, delete_action, filter_key_mapping={},
    ):
        self.system = system
        self.create_action = create_action
        self.read_action = read_action
        self.update_action = update_action
        self.delete_action = delete_action
        self.filter_key_mapping = filter_key_mapping

    @abc.abstractmethod
    def get_subject(self, bundle):
        raise NotImplementedError()

    @abc.abstractmethod
    def get_create_detail_resources(self, bundle):
        raise NotImplementedError()

    @abc.abstractclassmethod
    def get_create_detail_environment(self, bundle):
        raise NotImplementedError()

    @abc.abstractmethod
    def get_read_detail_resources(self, bundle):
        raise NotImplementedError()

    @abc.abstractclassmethod
    def get_read_detail_environment(self, bundle):
        raise NotImplementedError()

    @abc.abstractmethod
    def get_update_detail_resources(self, bundle):
        raise NotImplementedError()

    @abc.abstractclassmethod
    def get_update_detail_environment(self, bundle):
        raise NotImplementedError()

    @abc.abstractmethod
    def get_delete_detail_resources(self, bundle):
        raise NotImplementedError()

    @abc.abstractclassmethod
    def get_delete_detail_environment(self, bundle):
        raise NotImplementedError()

    @abc.abstractclassmethod
    def get_read_list_environment(self, bundle):
        raise NotImplementedError()


class IAMCreateAuthorizationMixin(object):
    def create_list(self, object_list, bundle):
        raise Unauthorized()

    def create_detail(self, object_list, bundle):
        system = self.helper.system
        subject = self.helper.get_subject(bundle)
        action = Action(self.helper.create_action)
        resources = self.helper.get_create_detail_resources(bundle)

        request = Request(system, subject, action, resources, self.helper.get_create_detail_environment(bundle),)

        allowed = self.iam.is_allowed(request)
        logger.debug("tastypie create_detail is_allowed request({}) result: {}".format(request.to_dict(), allowed))

        if not allowed:
            raise ImmediateHttpResponse(IAMAuthFailedResponse(AuthFailedException(system, subject, action, resources)))

        return allowed


class IAMUpdateAuthorizationMixin(object):
    def update_list(self, object_list, bundle):
        raise Unauthorized()

    def update_detail(self, object_list, bundle):
        system = self.helper.system
        subject = self.helper.get_subject(bundle)
        action = Action(self.helper.update_action)
        resources = self.helper.get_update_detail_resources(bundle)

        request = Request(system, subject, action, resources, self.helper.get_update_detail_environment(bundle),)

        allowed = self.iam.is_allowed(request)
        logger.debug("tastypie update_detail is_allowed request({}) result: {}".format(request.to_dict(), allowed))

        if not allowed:
            raise ImmediateHttpResponse(IAMAuthFailedResponse(AuthFailedException(system, subject, action, resources)))

        return allowed


class IAMDeleteAuthorizationMixin(object):
    def delete_list(self, object_list, bundle):
        raise Unauthorized()

    def delete_detail(self, object_list, bundle):
        system = self.helper.system
        subject = self.helper.get_subject(bundle)
        action = Action(self.helper.delete_action)
        resources = self.helper.get_delete_detail_resources(bundle)

        request = Request(system, subject, action, resources, self.helper.get_delete_detail_environment(bundle),)

        allowed = self.iam.is_allowed(request)
        logger.debug("tastypie delete_detail is_allowed request({}) result: {}".format(request.to_dict(), allowed))

        if not allowed:
            raise ImmediateHttpResponse(IAMAuthFailedResponse(AuthFailedException(system, subject, action, resources)))

        return allowed


class IAMReadDetailAuthorizationMixin(object):
    def read_detail(self, object_list, bundle):
        system = self.helper.system
        subject = self.helper.get_subject(bundle)
        action = Action(self.helper.read_action)
        resources = self.helper.get_read_detail_resources(bundle)

        request = Request(system, subject, action, resources, self.helper.get_read_detail_environment(bundle),)

        allowed = self.iam.is_allowed(request)
        logger.debug("tastypie read_detail is_allowed request({}) result: {}".format(request.to_dict(), allowed))

        if not allowed:
            raise ImmediateHttpResponse(IAMAuthFailedResponse(AuthFailedException(system, subject, action, resources)))

        return allowed


class IAMAuthorization(Authorization):
    def __init__(self, iam, helper):
        self.iam = iam
        self.helper = helper


class IAMReadOnlyAuthorization(ReadOnlyAuthorization):
    def __init__(self, iam, helper):
        self.iam = iam
        self.helper = helper


class ReadOnlyCompleteListIAMAuthorization(
    IAMReadDetailAuthorizationMixin, IAMReadOnlyAuthorization,
):
    def read_list(self, object_list, bundle):
        return object_list


class CustomCreateCompleteListIAMAuthorization(
    IAMUpdateAuthorizationMixin, IAMDeleteAuthorizationMixin, IAMReadDetailAuthorizationMixin, IAMAuthorization,
):
    def read_list(self, object_list, bundle):
        return object_list

    def create_detail(self, object_list, bundle):
        return True


class CompleteListIAMAuthorization(
    IAMCreateAuthorizationMixin,
    IAMUpdateAuthorizationMixin,
    IAMDeleteAuthorizationMixin,
    IAMReadDetailAuthorizationMixin,
    IAMAuthorization,
):
    def read_list(self, object_list, bundle):
        return object_list


class StrictListIAMAuthorization(
    IAMCreateAuthorizationMixin,
    IAMUpdateAuthorizationMixin,
    IAMDeleteAuthorizationMixin,
    IAMReadDetailAuthorizationMixin,
    IAMAuthorization,
):
    def read_list(self, object_list, bundle):
        request = Request(
            system=self.system,
            subject=self.get_subject(bundle),
            action=Action(self.read_action),
            resources=[],
            environment=self.get_read_list_environment(bundle),
        )
        f = self.iam.make_filter(request, key_mapping=self.helper.filter_key_mapping)
        logger.debug("tastypie read_list make_filter request({}) result: {}".format(request.to_dict(), f))
        return object_list.filter(f)
