# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
import logging

from iam import Subject, Action, MultiActionRequest
from iam.shortcuts import allow_or_raise_auth_failed

from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from gcloud import err_code
from gcloud.iam_auth import IAMMeta, get_iam_client

iam = get_iam_client()
iam_logger = logging.getLogger("iam")


class ApiMixin(GenericViewSet):
    EXEMPT_STATUS_CODES = {status.HTTP_204_NO_CONTENT}

    def finalize_response(self, request, response, *args, **kwargs):
        # 对rest_framework的Response进行统一处理
        if isinstance(response, Response):
            if response.exception is True:
                error = response.data.get(
                    "detail", ErrorDetail("Error from API exception", err_code.UNKNOWN_ERROR.code)
                )
                response.data = {"result": False, "data": response.data, "code": error.code, "message": str(error)}
            elif response.status_code not in self.EXEMPT_STATUS_CODES:
                response.data = {"result": True, "data": response.data, "code": err_code.SUCCESS.code, "message": ""}

        return super(ApiMixin, self).finalize_response(request, response, *args, **kwargs)


class IAMMixin:
    @staticmethod
    def iam_auth_check(request, action, resources):
        allow_or_raise_auth_failed(
            iam=iam,
            system=IAMMeta.SYSTEM_ID,
            subject=Subject("user", request.user.username),
            action=Action(action),
            resources=resources,
        )

    def iam_get_instances_auth_actions(self, request, instances):
        helper = getattr(self, "iam_resource_helper", None)
        if not helper:
            return None

        # 1. collect resources
        resources_list = []
        for instance in instances:
            resources_list.append(helper.get_resources(instance))

        if not resources_list:
            return None

        # 2. make request
        request = MultiActionRequest(
            helper.system,
            helper.get_subject_for_alter_list(request, instances),
            [Action(action) for action in helper.actions],
            [],
            helper.get_environment_for_alter_list(request, instances),
        )

        resource_actions_allowed = helper.iam.batch_resource_multi_actions_allowed(request, resources_list)
        iam_logger.debug(
            "[drf iam_get_instances_auth_actions] batch_resource_multi_actions_allowed request({}) result: {}".format(
                request.to_dict(), resource_actions_allowed
            )
        )

        # 3. assemble action allowed data
        auth_actions = dict()
        for instance in instances:
            rid = str(helper.get_resources_id(instance))
            auth_actions[instance.id] = [
                action for action, allowed in resource_actions_allowed.get(rid, {}).items() if allowed
            ]

        return auth_actions

    def iam_get_instance_auth_actions(self, request, instance):
        helper = getattr(self, "iam_resource_helper", None)
        if not helper:
            return None

        # 1. get resources
        resources = helper.get_resources(instance)

        # 2. make request
        request = MultiActionRequest(
            helper.system,
            helper.get_subject_for_alter_detail(request, instance),
            [Action(action) for action in helper.actions],
            resources,
            helper.get_environment_for_alter_detail(request, instance),
        )

        actions_allowed = helper.iam.resource_multi_actions_allowed(request)
        iam_logger.debug(
            "[drf iam_get_instance_auth_actions] resource_multi_actions_allowed request({}) result: {}".format(
                request.to_dict(), actions_allowed
            )
        )

        # 3. assemble action allowed data
        auth_actions = [action for action, allowed in actions_allowed.items() if allowed]

        return auth_actions
