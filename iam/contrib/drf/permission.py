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
import logging

import six
from rest_framework import permissions

from iam import Action, Request
from iam.exceptions import AuthFailedException

logger = logging.getLogger("iam")


@six.add_metaclass(abc.ABCMeta)
class IAMPermissionHelper(object):
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
    def get_subject(self, request, obj=None):
        raise NotImplementedError()

    @abc.abstractmethod
    def get_create_resources(self, request):
        raise NotImplementedError()

    @abc.abstractclassmethod
    def get_create_environment(self, request):
        raise NotImplementedError()

    @abc.abstractmethod
    def get_retrieve_resources(self, request, obj):
        raise NotImplementedError()

    @abc.abstractclassmethod
    def get_retrieve_environment(self, request, obj):
        raise NotImplementedError()

    @abc.abstractmethod
    def get_update_resources(self, request, obj):
        raise NotImplementedError()

    @abc.abstractclassmethod
    def get_update_environment(self, request, obj):
        raise NotImplementedError()

    @abc.abstractmethod
    def get_destroy_resources(self, request, obj):
        raise NotImplementedError()

    @abc.abstractclassmethod
    def get_destroy_environment(self, request, obj):
        raise NotImplementedError()

    @abc.abstractclassmethod
    def get_list_environment(self, request):
        raise NotImplementedError()


class IAMPermission(permissions.BasePermission):
    def __init__(self, iam, helper):
        self.iam = iam
        self.helper = helper
        self.message = "iam permission failed"

    def has_permission(self, request, view):
        if view.action == "list":
            return self.check_list_permission(request)

        if view.action == "create":
            return self.check_create_permission(request)

        if view.action in ["retrieve", "update", "partial_update", "destroy"]:
            # 交给 has_object_permission 做校验
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if view.action == "retrieve":
            return self.check_retrieve_permission(request, obj)
        if view.action in ["update", "partial_update"]:
            return self.check_update_permission(request, obj)
        if view.action == "destroy":
            return self.check_destroy_permission(request, obj)
        return False

    def check_list_permission(self, request):
        # list 操作默认不鉴权
        return True

    def check_create_permission(self, request):
        system = self.helper.system
        subject = self.helper.get_subject(request)
        action = Action(self.helper.create_action)
        resources = self.helper.get_create_resources(request)

        iam_request = Request(system, subject, action, resources, self.helper.get_create_environment(request),)

        allowed = self.iam.is_allowed(iam_request)
        logger.debug(
            "drf check_create_permission is_allowed request({}) " "result: {}".format(iam_request.to_dict(), allowed)
        )

        if not allowed:
            raise AuthFailedException(system, subject, action, resources)

        return allowed

    def check_retrieve_permission(self, request, obj):
        system = self.helper.system
        subject = self.helper.get_subject(request)
        action = Action(self.helper.read_action)
        resources = self.helper.get_retrieve_resources(request, obj)

        iam_request = Request(system, subject, action, resources, self.helper.get_retrieve_environment(request, obj),)

        allowed = self.iam.is_allowed(iam_request)
        logger.debug(
            "drf check_retrieve_permission is_allowed request({}) " "result: {}".format(iam_request.to_dict(), allowed)
        )

        if not allowed:
            raise AuthFailedException(system, subject, action, resources)

        return allowed

    def check_update_permission(self, request, obj):
        system = self.helper.system
        subject = self.helper.get_subject(request, obj)
        action = Action(self.helper.update_action)
        resources = self.helper.get_update_resources(request, obj)

        iam_request = Request(system, subject, action, resources, self.helper.get_update_environment(request, obj),)

        allowed = self.iam.is_allowed(iam_request)
        logger.debug(
            "drf check_update_permission is_allowed request({}) " "result: {}".format(iam_request.to_dict(), allowed)
        )

        if not allowed:
            raise AuthFailedException(system, subject, action, resources)

        return allowed

    def check_destroy_permission(self, request, obj):
        system = self.helper.system
        subject = self.helper.get_subject(request, obj)
        action = Action(self.helper.delete_action)
        resources = self.helper.get_destroy_resources(request, obj)

        iam_request = Request(system, subject, action, resources, self.helper.get_destroy_environment(request, obj),)

        allowed = self.iam.is_allowed(iam_request)
        logger.debug(
            "drf check_destroy_permission is_allowed request({}) " "result: {}".format(iam_request.to_dict(), allowed)
        )

        if not allowed:
            raise AuthFailedException(system, subject, action, resources)

        return allowed
