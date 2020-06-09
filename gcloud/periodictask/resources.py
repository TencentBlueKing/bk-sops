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

import logging
import traceback

import ujson as json
from tastypie import fields
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from tastypie.exceptions import BadRequest, NotFound
from tastypie.authorization import ReadOnlyAuthorization
from djcelery.models import PeriodicTask as CeleryTask

from pipeline.exceptions import PipelineException
from pipeline.contrib.periodic_task.models import PeriodicTask as PipelinePeriodicTask
from pipeline_web.parser.validator import validate_web_pipeline_tree

from iam import Resource, Subject, Action
from iam.contrib.tastypie.shortcuts import allow_or_raise_immediate_response
from iam.contrib.tastypie.authorization import CustomCreateCompleteListIAMAuthorization

from gcloud.constants import PROJECT, COMMON
from gcloud.tasktmpl3.models import TaskTemplate
from gcloud.periodictask.models import PeriodicTask
from gcloud.utils.strings import name_handler
from gcloud.core.constant import PERIOD_TASK_NAME_MAX_LENGTH
from gcloud.core.resources import ProjectResource
from gcloud.commons.template.models import replace_template_id, CommonTemplate
from gcloud.commons.tastypie import GCloudModelResource
from gcloud.iam_auth import IAMMeta, get_iam_client
from gcloud.iam_auth.resource_helpers import PeriodicTaskResourceHelper
from gcloud.iam_auth.authorization_helpers import PeriodicTaskIAMAuthorizationHelper

logger = logging.getLogger("root")
iam = get_iam_client()


class CeleryTaskResource(GCloudModelResource):
    enabled = fields.BooleanField(attribute="enabled", readonly=True)

    class Meta(GCloudModelResource.Meta):
        queryset = CeleryTask.objects.all()
        authorization = ReadOnlyAuthorization()
        resource_name = "celery_task"
        filtering = {
            "enabled": ALL,
        }


class PipelinePeriodicTaskResource(GCloudModelResource):
    celery_task = fields.ForeignKey(CeleryTaskResource, "celery_task", full=True)
    name = fields.CharField(attribute="name", readonly=True)
    creator = fields.CharField(attribute="creator", readonly=True)

    class Meta(GCloudModelResource.Meta):
        queryset = PipelinePeriodicTask.objects.all()
        authorization = ReadOnlyAuthorization()
        resource_name = "pipeline_periodic_task"
        filtering = {
            "name": ALL,
            "creator": ALL,
            "celery_task": ALL_WITH_RELATIONS,
        }


class PeriodicTaskResource(GCloudModelResource):
    project = fields.ForeignKey(ProjectResource, "project", full=True)
    task_template_name = fields.CharField(attribute="task_template_name", readonly=True)
    template_id = fields.CharField(attribute="template_id", readonly=True)
    enabled = fields.BooleanField(attribute="enabled", readonly=True)
    name = fields.CharField(attribute="name", readonly=True)
    cron = fields.CharField(attribute="cron", readonly=True)
    total_run_count = fields.IntegerField(attribute="total_run_count", readonly=True)
    last_run_at = fields.DateTimeField(attribute="last_run_at", readonly=True, null=True)
    creator = fields.CharField(attribute="creator", readonly=True)
    pipeline_tree = fields.DictField(attribute="pipeline_tree", readonly=True, use_in="detail")
    form = fields.DictField(attribute="form", readonly=True, use_in="detail")
    task = fields.ForeignKey(PipelinePeriodicTaskResource, "task", full=True)

    class Meta(GCloudModelResource.Meta):
        queryset = PeriodicTask.objects.all()
        resource_name = "periodic_task"
        filtering = {
            "id": ALL,
            "template_id": ALL,
            "template_source": ALL,
            "project": ALL_WITH_RELATIONS,
            "name": ALL,
            "enabled": ALL,
            "creator": ALL,
            "task": ALL_WITH_RELATIONS,
        }
        # iam config
        authorization = CustomCreateCompleteListIAMAuthorization(
            iam=iam,
            helper=PeriodicTaskIAMAuthorizationHelper(
                system=IAMMeta.SYSTEM_ID,
                create_action=None,
                read_action=IAMMeta.PERIODIC_TASK_VIEW_ACTION,
                update_action=IAMMeta.PERIODIC_TASK_EDIT_ACTION,
                delete_action=IAMMeta.PERIODIC_TASK_DELETE_ACTION,
            ),
        )
        iam_resource_helper = PeriodicTaskResourceHelper(
            iam=iam,
            system=IAMMeta.SYSTEM_ID,
            actions=[
                IAMMeta.PERIODIC_TASK_VIEW_ACTION,
                IAMMeta.PERIODIC_TASK_EDIT_ACTION,
                IAMMeta.PERIODIC_TASK_DELETE_ACTION,
            ],
        )

    def obj_create(self, bundle, **kwargs):
        try:
            template_id = bundle.data.pop("template_id")
            template_source = bundle.data.get("template_source", PROJECT)
            name = bundle.data.pop("name")
            cron = json.loads(bundle.data.pop("cron"))
            pipeline_tree = json.loads(bundle.data.pop("pipeline_tree"))
        except (KeyError, ValueError) as e:
            message = "create periodic_task params error: %s" % e.message
            logger.error(message)
            raise BadRequest(message)

        if not isinstance(cron, dict):
            raise BadRequest("cron must be a object json string")

        try:
            project = ProjectResource().get_via_uri(bundle.data.get("project"), request=bundle.request)
        except NotFound:
            raise BadRequest("project [uri=%s] does not exist" % bundle.data.get("project"))

        if template_source == PROJECT:
            try:
                template = TaskTemplate.objects.get(id=template_id, project=project, is_deleted=False)
            except TaskTemplate.DoesNotExist:
                raise BadRequest(
                    "template[id={template_id}] of project[{project_id}] does not exist".format(
                        template_id=template_id, project_id=project.id
                    )
                )

            allow_or_raise_immediate_response(
                iam=iam,
                system=IAMMeta.SYSTEM_ID,
                subject=Subject("user", bundle.request.user.username),
                action=Action(IAMMeta.FLOW_CREATE_PERIODIC_TASK_ACTION),
                resources=[
                    Resource(
                        system=IAMMeta.SYSTEM_ID,
                        type=IAMMeta.FLOW_RESOURCE,
                        id=str(template.id),
                        attribute={"iam_resource_owner": template.creator, "name": template.name},
                    )
                ],
            )

            try:
                replace_template_id(TaskTemplate, pipeline_tree)
            except TaskTemplate.DoesNotExist:
                raise BadRequest("invalid subprocess, check subprocess node please")

        elif template_source == COMMON:
            try:
                template = CommonTemplate.objects.get(id=template_id, is_deleted=False)
            except CommonTemplate.DoesNotExist:
                raise BadRequest("common template[id=%s] does not exist" % template_id)

            allow_or_raise_immediate_response(
                iam=iam,
                system=IAMMeta.SYSTEM_ID,
                subject=Subject("user", bundle.request.user.username),
                action=Action(IAMMeta.COMMON_FLOW_CREATE_PERIODIC_TASK_ACTION),
                resources=[
                    Resource(system=IAMMeta.SYSTEM_ID, type=IAMMeta.PROJECT_RESOURCE, id=str(project.id), attribute={}),
                    Resource(
                        system=IAMMeta.SYSTEM_ID,
                        type=IAMMeta.COMMON_FLOW_RESOURCE,
                        id=str(template.id),
                        attribute={"iam_resource_owner": template.creator, "name": template.name},
                    ),
                ],
            )

            try:
                replace_template_id(CommonTemplate, pipeline_tree)
            except TaskTemplate.DoesNotExist:
                raise BadRequest("invalid subprocess, check subprocess node please")

        else:
            raise BadRequest("invalid template_source[%s]" % template_source)

        # XSS handle
        name = name_handler(name, PERIOD_TASK_NAME_MAX_LENGTH)
        creator = bundle.request.user.username

        # validate pipeline tree
        try:
            validate_web_pipeline_tree(pipeline_tree)
        except PipelineException as e:
            raise BadRequest(str(e))

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
            raise BadRequest(str(e))

        response = super(PeriodicTaskResource, self).obj_create(bundle, **kwargs)
        response.obj.set_enabled(True)

        return response
