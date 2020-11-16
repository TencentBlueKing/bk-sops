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

from iam import MultiActionRequest, Action

logger = logging.getLogger("iam")


@six.add_metaclass(abc.ABCMeta)
class IAMResourceHelper(object):
    """
    helper 对应函数中的 obj 可为 实例对象 或 字典对象
    实现时需根据 IAMResourceMixin 中 handler 处理函数的调用位置确定
    """

    def __init__(self, iam, system, actions):
        self.iam = iam
        self.system = system
        self.actions = actions

    @abc.abstractmethod
    def get_resources(self, obj):
        raise NotImplementedError()

    @abc.abstractmethod
    def get_resources_id(self, obj):
        raise NotImplementedError()

    @abc.abstractmethod
    def get_subject_for_list(self, request, obj_list):
        raise NotImplementedError()

    @abc.abstractmethod
    def get_environment_for_list(self, request, obj_list):
        raise NotImplementedError()

    @abc.abstractmethod
    def get_subject_for_detail(self, request, obj):
        raise NotImplementedError()

    @abc.abstractmethod
    def get_environment_for_detail(self, request, obj):
        raise NotImplementedError()


class IAMResourceMixin(object):
    def iam_list_handler(self, request, obj_list, is_serialized):
        """
        is_serialized 为 True, 则 obj_list 中的obj都是序列化后的字典对象
        is_serialized 为 False, 则 obj_list 中的obj都是实例对象
        """
        helper = getattr(self._meta, "iam_resource_helper", None)
        if not helper:
            return obj_list

        # 1. collect resources
        resources_list = [helper.get_resources(obj) for obj in obj_list]
        if not resources_list:
            return obj_list

        # 2. make request
        iam_request = MultiActionRequest(
            helper.system,
            helper.get_subject_for_list(request, obj_list),
            [Action(action) for action in helper.actions],
            [],
            helper.get_environment_for_list(request, obj_list),
        )

        resource_actions_allowed = helper.iam.batch_resource_multi_actions_allowed(iam_request, resources_list)
        logger.debug(
            "drf iam_list_handler batch_resource_multi_actions_allowed request({}) result: {}".format(
                iam_request.to_dict(), resource_actions_allowed
            )
        )

        # 3. assemble action allowed data
        for obj in obj_list:
            rid = str(helper.get_resources_id(obj))
            auth_actions = [action for action, allowed in resource_actions_allowed.get(rid, {}).items() if allowed]
            self._save_obj_auth_actions(obj, auth_actions, is_serialized)
        return obj_list

    def iam_detail_handler(self, request, obj, is_serialized):
        helper = getattr(self._meta, "iam_resource_helper", None)
        if not helper:
            return obj

        # 1. get resources
        resources = helper.get_resources(obj)

        # 2. make request
        request = MultiActionRequest(
            helper.system,
            helper.get_subject_for_detail(request, obj),
            [Action(action) for action in helper.actions],
            resources,
            helper.get_environment_for_detail(request, obj),
        )

        actions_allowed = helper.iam.resource_multi_actions_allowed(request)
        logger.debug(
            "drf iam_detail_handler resource_multi_actions_allowed request({}) result: {}".format(
                request.to_dict(), actions_allowed
            )
        )

        # 3. assemble action allowed data
        auth_actions = [action for action, allowed in actions_allowed.items() if allowed]
        self._save_obj_auth_actions(obj, auth_actions, is_serialized)

        return obj

    @staticmethod
    def _save_obj_auth_actions(obj, auth_actions, is_serialized):
        """
        根据接收到的 obj 是否序列化来保存对应的认证操作
        is_serialized 为 False 则 obj 是实例对象
        is_serialized 为 True 则 obj 是字典对象
        """
        if is_serialized:
            obj["auth_actions"] = auth_actions
        else:
            setattr(obj, "auth_actions", auth_actions)
