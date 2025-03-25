# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
import logging

from django.conf import settings
from iam import Action, MultiActionRequest, Subject
from iam.shortcuts import allow_or_raise_auth_failed
from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from gcloud import err_code
from gcloud.core.models import Project
from gcloud.iam_auth import IAMMeta, get_iam_client

iam = get_iam_client()
iam_logger = logging.getLogger("iam")
logger = logging.getLogger("root")


class ApiMixin(GenericViewSet):
    EXEMPT_STATUS_CODES = {status.HTTP_204_NO_CONTENT}

    @staticmethod
    def _extract_error_detail_string(original_error):
        if isinstance(original_error, ErrorDetail):
            return str(original_error)
        elif isinstance(original_error, dict):
            errors = []
            for error in original_error.values():
                if isinstance(error, list):
                    errors.extend(error)
                else:
                    errors.append(error)
            return ",".join([str(e) for e in errors if isinstance(e, ErrorDetail)])
        else:
            return original_error

    def finalize_response(self, request, response, *args, **kwargs):
        # 对rest_framework的Response进行统一处理
        if isinstance(response, Response):
            if response.exception is True:
                error = (
                    response.data.get("detail")
                    or response.data
                    or ErrorDetail("Error from API exception", err_code.UNKNOWN_ERROR.code)
                )
                error_code = getattr(error, "code", err_code.UNKNOWN_ERROR.code)
                logger.error(
                    f"[ApiMixin response exception] request: {request.path}, "
                    f"params: {request.query_params or request.data}, response: {response.data}"
                )
                response.data = {
                    "result": False,
                    "data": response.data,
                    "code": error_code,
                    "message": self._extract_error_detail_string(error) or str(error),
                }
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


class MultiTenantMixin:
    model_multi_tenant_filter = False
    project_multi_tenant_filter = False
    project_id_multi_tenant_filter = False
    taskflow_multi_tenant_filter = False

    def get_queryset(self):
        queryset = super().get_queryset()
        if settings.ENABLE_MULTI_TENANT_MODE:
            tenant_id = self.request.user.tenant_id
            if self.model_multi_tenant_filter:
                queryset = queryset.filter(tenant_id=tenant_id)
            elif self.project_multi_tenant_filter:
                queryset = queryset.filter(project__tenant_id=tenant_id)
            elif self.project_id_multi_tenant_filter:
                project_ids = Project.objects.filter(tenant_id=tenant_id).values_list("id", flat=True)
                queryset = queryset.filter(project_id__in=project_ids)
            elif self.taskflow_multi_tenant_filter:
                queryset = queryset.filter(task__project__tenant_id=tenant_id)
        return queryset
