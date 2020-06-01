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

from iam import Action, MultiActionRequest

logger = logging.getLogger("iam")


@six.add_metaclass(abc.ABCMeta)
class IAMResourceHelper(object):
    def __init__(self, iam, system, actions):
        self.iam = iam
        self.system = system
        self.actions = actions

    @abc.abstractmethod
    def get_resources(self, bundle):
        raise NotImplementedError()

    @abc.abstractmethod
    def get_resources_id(self, bundle):
        raise NotImplementedError()

    @abc.abstractmethod
    def get_subject_for_alter_list(self, request, data):
        raise NotImplementedError()

    @abc.abstractmethod
    def get_environment_for_alter_list(self, request, data):
        raise NotImplementedError()

    @abc.abstractmethod
    def get_subject_for_alter_detail(self, request, data):
        raise NotImplementedError()

    @abc.abstractmethod
    def get_environment_for_alter_detail(self, request, data):
        raise NotImplementedError()


class IAMResourceMixin(object):
    def alter_list_data_to_serialize(self, request, data):
        helper = getattr(self._meta, "iam_resource_helper", None)
        if not helper:
            return data

        # 1. collect resources
        resources_list = []
        for bundle in data["objects"]:
            resources_list.append(helper.get_resources(bundle))

        if not resources_list:
            return data

        # 2. make request
        request = MultiActionRequest(
            helper.system,
            helper.get_subject_for_alter_list(request, data),
            [Action(action) for action in helper.actions],
            [],
            helper.get_environment_for_alter_list(request, data),
        )

        resource_actions_allowed = helper.iam.batch_resource_multi_actions_allowed(request, resources_list)
        logger.debug(
            "tastypie alter_list_data_to_serialize batch_resource_multi_actions_allowed request({}) result: {}".format(
                request.to_dict(), resource_actions_allowed
            )
        )

        # 3. assemble action allowed data
        for bundle in data["objects"]:
            rid = str(helper.get_resources_id(bundle))
            bundle.data["auth_actions"] = [
                action for action, allowed in resource_actions_allowed.get(rid, {}).items() if allowed
            ]

        return data

    def alter_detail_data_to_serialize(self, request, data):
        helper = getattr(self._meta, "iam_resource_helper", None)
        if not helper:
            return data

        bundle = data

        # 1. get resources
        resources = helper.get_resources(bundle)

        # 2. make request
        request = MultiActionRequest(
            helper.system,
            helper.get_subject_for_alter_detail(request, data),
            [Action(action) for action in helper.actions],
            resources,
            helper.get_environment_for_alter_detail(request, data),
        )

        actions_allowed = helper.iam.resource_multi_actions_allowed(request)
        logger.debug(
            "tastypie alter_detail_data_to_serialize resource_multi_actions_allowed request({}) result: {}".format(
                request.to_dict(), actions_allowed
            )
        )

        # 3. assemble action allowed data
        bundle.data["auth_actions"] = [action for action, allowed in actions_allowed.items() if allowed]

        return data
