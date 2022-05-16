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

from rest_framework import mixins, status, permissions
from rest_framework.response import Response
from rest_framework.exceptions import ErrorDetail
from rest_framework.pagination import LimitOffsetPagination

from pipeline_web.parser.validator import validate_web_pipeline_tree
from pipeline.exceptions import PipelineException

from gcloud import err_code
from gcloud.periodictask.models import PeriodicTask
from gcloud.constants import PROJECT, COMMON, PERIOD_TASK_NAME_MAX_LENGTH
from gcloud.tasktmpl3.models import TaskTemplate
from gcloud.common_template.models import CommonTemplate
from gcloud.template_base.utils import replace_template_id
from gcloud.utils.strings import standardize_name
from gcloud.core.apis.drf.viewsets.base import GcloudReadOnlyViewSet
from gcloud.core.apis.drf.serilaziers.periodic_task import PeriodicTaskSerializer, CreatePeriodicTaskSerializer
from gcloud.core.apis.drf.resource_helpers import ViewSetResourceHelper
from gcloud.iam_auth import res_factory
from gcloud.iam_auth import IAMMeta
from gcloud.core.apis.drf.filtersets import AllLookupSupportFilterSet
from gcloud.core.apis.drf.permission import (
    HAS_OBJECT_PERMISSION,
    IamPermission,
    IamPermissionInfo,
    IamUserTypeBasedValidator,
)

logger = logging.getLogger("root")


class PeriodicTaskPermission(IamPermission):
    actions = {
        "retrieve": IamPermissionInfo(
            IAMMeta.PERIODIC_TASK_VIEW_ACTION, res_factory.resources_for_periodic_task_obj, HAS_OBJECT_PERMISSION
        ),
        "destroy": IamPermissionInfo(
            IAMMeta.PERIODIC_TASK_DELETE_ACTION, res_factory.resources_for_periodic_task_obj, HAS_OBJECT_PERMISSION
        ),
    }

    def has_permission(self, request, view):
        if view.action == "list":
            user_type_validator = IamUserTypeBasedValidator()
            return user_type_validator.validate(request)
        elif view.action == "create":
            template_source = request.data.get("template_source", PROJECT)
            template_id = request.data.get("template_id")
            if template_source == PROJECT:
                iam_action = IAMMeta.FLOW_CREATE_PERIODIC_TASK_ACTION
                resources = res_factory.resources_for_flow(template_id)
            else:
                iam_action = IAMMeta.COMMON_FLOW_CREATE_PERIODIC_TASK_ACTION
                resources = res_factory.resources_for_common_flow(template_id)
                if request.data.get("project"):
                    resources.extend(res_factory.resources_for_project(request.data["project"]))
            self.iam_auth_check(
                request=request, action=iam_action, resources=resources,
            )
            return True
        return super().has_permission(request, view)


class PeriodicTaskFilter(AllLookupSupportFilterSet):
    class Meta:
        model = PeriodicTask
        fields = {"task__celery_task__enabled": ["exact"], "task__creator": ["contains"], "project__id": ["exact"]}


class PeriodicTaskViewSet(GcloudReadOnlyViewSet, mixins.CreateModelMixin, mixins.DestroyModelMixin):
    queryset = PeriodicTask.objects.all()
    serializer_class = PeriodicTaskSerializer
    filter_class = PeriodicTaskFilter
    pagination_class = LimitOffsetPagination
    iam_resource_helper = ViewSetResourceHelper(
        resource_func=res_factory.resources_for_periodic_task_obj,
        actions=[
            IAMMeta.PERIODIC_TASK_VIEW_ACTION,
            IAMMeta.PERIODIC_TASK_EDIT_ACTION,
            IAMMeta.PERIODIC_TASK_DELETE_ACTION,
        ],
    )
    permission_classes = [permissions.IsAuthenticated, PeriodicTaskPermission]

    def create(self, request, *args, **kwargs):
        serializer = CreatePeriodicTaskSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        template_source = serializer.validated_data["template_source"]
        template_id = serializer.validated_data["template_id"]
        project = serializer.validated_data["project"]
        pipeline_tree = serializer.validated_data["pipeline_tree"]
        name = serializer.validated_data["name"]
        if template_source == PROJECT:
            model_cls = TaskTemplate
            condition = {"id": template_id, "project": project, "is_deleted": False}
        elif template_source == COMMON:
            model_cls = CommonTemplate
            condition = {"id": template_id, "is_deleted": False}
        else:
            message = "invalid template_source[%s]" % template_source
            return Response({"detail": ErrorDetail(message, err_code.REQUEST_PARAM_INVALID.code)}, exception=True)

        try:
            template = model_cls.objects.filter(**condition).first()
        except model_cls.DoesNotExist:
            message = "common template[id=%s] does not exist" % template_id
            return Response({"detail": ErrorDetail(message, err_code.REQUEST_PARAM_INVALID.code)}, exception=True)
        try:
            replace_template_id(model_cls, pipeline_tree)
        except model_cls.DoesNotExist:
            message = "invalid subprocess, check subprocess node please"
            return Response({"detail": ErrorDetail(message, err_code.REQUEST_PARAM_INVALID.code)}, exception=True)

        # XSS handle
        name = standardize_name(name, PERIOD_TASK_NAME_MAX_LENGTH)
        creator = request.user.username

        # validate pipeline tree
        try:
            validate_web_pipeline_tree(pipeline_tree)
        except PipelineException as e:
            message = str(e)
            return Response({"detail": ErrorDetail(message, err_code.REQUEST_PARAM_INVALID.code)}, exception=True)

        serializer.validated_data["template"] = template
        serializer.validated_data["creator"] = creator
        serializer.validated_data["name"] = name
        serializer.validated_data["project"] = project
        serializer.validated_data["template_source"] = template_source

        instance = serializer.save()
        instance.set_enabled(True)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
