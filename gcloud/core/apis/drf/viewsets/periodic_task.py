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
import traceback

from rest_framework import mixins, status
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
from gcloud.core.apis.drf.viewsets.base import GcloudListViewSet
from gcloud.core.apis.drf.serilaziers.periodic_task import PeriodicTaskSerializer, CreatePeriodicTaskSerializer
from gcloud.core.apis.drf.resource_helpers import ViewSetResourceHelper
from gcloud.iam_auth import res_factory
from gcloud.iam_auth import IAMMeta
from gcloud.core.apis.drf.filtersets import AllLookupSupportFilterSet


logger = logging.getLogger("root")


class PeriodicTaskFilter(AllLookupSupportFilterSet):
    class Meta:
        model = PeriodicTask
        fields = {"task__celery_task__enabled": ["exact"], "task__creator": ["contains"], "project__id": ["exact"]}


class PeriodicTaskViewSet(GcloudListViewSet, mixins.CreateModelMixin):
    queryset = PeriodicTask.objects.all()
    serializer_class = PeriodicTaskSerializer
    create_serializer_class = CreatePeriodicTaskSerializer
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

    def create(self, request, *args, **kwargs):
        serializer = self.create_serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        template_source = serializer.validated_data["template_source"]
        template_id = serializer.validated_data["template_id"]
        project = serializer.validated_data["project"]
        pipeline_tree = serializer.validated_data["pipeline_tree"]
        cron = serializer.validated_data["cron"]
        name = serializer.validated_data["name"]
        if template_source == PROJECT:
            try:
                template = TaskTemplate.objects.get(id=template_id, project=project, is_deleted=False)
            except TaskTemplate.DoesNotExist:
                message = "template[id={template_id}] of project[{project_id}] does not exist".format(
                    template_id=template_id, project_id=project.id
                )
                return Response({"detail": ErrorDetail(message, err_code.REQUEST_PARAM_INVALID.code)}, exception=True)

            try:
                replace_template_id(TaskTemplate, pipeline_tree)
            except TaskTemplate.DoesNotExist:
                message = "invalid subprocess, check subprocess node please"
                return Response({"detail": ErrorDetail(message, err_code.REQUEST_PARAM_INVALID.code)}, exception=True)

        elif template_source == COMMON:
            try:
                template = CommonTemplate.objects.get(id=template_id, is_deleted=False)
            except CommonTemplate.DoesNotExist:
                message = "common template[id=%s] does not exist" % template_id
                return Response({"detail": ErrorDetail(message, err_code.REQUEST_PARAM_INVALID.code)}, exception=True)

            try:
                replace_template_id(CommonTemplate, pipeline_tree)
            except TaskTemplate.DoesNotExist:
                message = "invalid subprocess, check subprocess node please"
                return Response({"detail": ErrorDetail(message, err_code.REQUEST_PARAM_INVALID.code)}, exception=True)

        else:
            message = "invalid template_source[%s]" % template_source
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

        kwargs["template_id"] = template_id
        kwargs["template_source"] = template_source
        try:
            kwargs["task"] = PeriodicTask.objects.create_pipeline_task(
                project=project,
                template=template,
                name=name,
                cron=cron,
                pipeline_tree=pipeline_tree,
                creator=creator,
                template_source=template_source,
            )
        except Exception as e:
            logger.warning(traceback.format_exc())
            message = str(e)
            return Response({"detail": ErrorDetail(message, err_code.REQUEST_PARAM_INVALID.code)}, exception=True)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
