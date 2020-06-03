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

import ujson as json
from django.contrib.auth import get_user_model
from django.db import transaction
from tastypie import fields
from tastypie.authorization import Authorization
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from tastypie.exceptions import BadRequest, InvalidFilterError

from pipeline.exceptions import PipelineException
from pipeline.models import TemplateScheme
from pipeline.validators.base import validate_pipeline_tree
from pipeline_web.parser.validator import validate_web_pipeline_tree

from iam import Resource, Subject, Action
from iam.shortcuts import allow_or_raise_auth_failed
from iam.contrib.tastypie.authorization import CompleteListIAMAuthorization

from gcloud.commons.template.resources import PipelineTemplateResource
from gcloud.core.constant import TEMPLATE_NODE_NAME_MAX_LENGTH
from gcloud.utils.strings import name_handler, pipeline_node_name_handle
from gcloud.tasktmpl3.models import TaskTemplate
from gcloud.commons.tastypie import GCloudModelResource, TemplateFilterPaginator
from gcloud.core.resources import ProjectResource
from gcloud.iam_auth import IAMMeta, get_iam_client
from gcloud.iam_auth.resource_helpers import SimpleResourceHelper
from gcloud.iam_auth.authorization_helpers import FlowIAMAuthorizationHelper

logger = logging.getLogger("root")
iam = get_iam_client()


class TaskTemplateResource(GCloudModelResource):
    project = fields.ForeignKey(ProjectResource, "project", full=True)
    pipeline_template = fields.ForeignKey(PipelineTemplateResource, "pipeline_template")
    name = fields.CharField(attribute="name", readonly=True, null=True)
    category_name = fields.CharField(attribute="category_name", readonly=True, null=True)
    creator_name = fields.CharField(attribute="creator_name", readonly=True, null=True)
    editor_name = fields.CharField(attribute="editor_name", readonly=True, null=True)
    create_time = fields.DateTimeField(attribute="create_time", readonly=True, null=True)
    edit_time = fields.DateTimeField(attribute="edit_time", readonly=True, null=True)
    pipeline_tree = fields.DictField(attribute="pipeline_tree", use_in="detail", readonly=True, null=True)
    template_id = fields.IntegerField(attribute="template_id", readonly=True)
    subprocess_info = fields.DictField(attribute="subprocess_info", use_in="detail", readonly=True)
    version = fields.CharField(attribute="version", readonly=True, null=True)
    subprocess_has_update = fields.BooleanField(attribute="subprocess_has_update", use_in="list", readonly=True)
    has_subprocess = fields.BooleanField(attribute="has_subprocess", readonly=True)

    class Meta(GCloudModelResource.Meta):
        queryset = TaskTemplate.objects.filter(pipeline_template__isnull=False, is_deleted=False)
        resource_name = "template"

        filtering = {
            "id": ALL,
            "project": ALL_WITH_RELATIONS,
            "name": ALL,
            "category": ALL,
            "pipeline_template": ALL_WITH_RELATIONS,
            "subprocess_has_update": ALL,
            "has_subprocess": ALL,
        }
        q_fields = ["id", "pipeline_template__name"]
        paginator_class = TemplateFilterPaginator
        # iam config
        authorization = CompleteListIAMAuthorization(
            iam=iam,
            helper=FlowIAMAuthorizationHelper(
                system=IAMMeta.SYSTEM_ID,
                create_action=IAMMeta.FLOW_CREATE_ACTION,
                read_action=IAMMeta.FLOW_VIEW_ACTION,
                update_action=IAMMeta.FLOW_EDIT_ACTION,
                delete_action=IAMMeta.FLOW_DELETE_ACTION,
            ),
        )
        iam_resource_helper = SimpleResourceHelper(
            type=IAMMeta.FLOW_RESOURCE,
            id_field="id",
            creator_field="creator_name",
            iam=iam,
            system=IAMMeta.SYSTEM_ID,
            actions=[
                IAMMeta.FLOW_VIEW_ACTION,
                IAMMeta.FLOW_EDIT_ACTION,
                IAMMeta.FLOW_DELETE_ACTION,
                IAMMeta.FLOW_CREATE_TASK_ACTION,
                IAMMeta.FLOW_CREATE_MINI_APP_ACTION,
                IAMMeta.FLOW_CREATE_PERIODIC_TASK_ACTION,
            ],
        )

    @staticmethod
    def handle_template_name_attr(data):
        data["name"] = name_handler(data["name"], TEMPLATE_NODE_NAME_MAX_LENGTH)
        pipeline_node_name_handle(data["pipeline_tree"])

    def dehydrate_pipeline_tree(self, bundle):
        return json.dumps(bundle.data["pipeline_tree"])

    def alter_list_data_to_serialize(self, request, data):
        data = super(TaskTemplateResource, self).alter_list_data_to_serialize(request, data)
        user_model = get_user_model()
        user = request.user
        collected_templates = (
            user_model.objects.get(username=user.username).tasktemplate_set.all().values_list("id", flat=True)
        )
        for bundle in data["objects"]:
            if bundle.obj.id in collected_templates:
                bundle.data["is_add"] = 1
            else:
                bundle.data["is_add"] = 0

        return data

    def obj_create(self, bundle, **kwargs):
        model = bundle.obj.__class__
        try:
            pipeline_template_kwargs = {
                "name": bundle.data.pop("name"),
                "creator": bundle.request.user.username,
                "pipeline_tree": json.loads(bundle.data.pop("pipeline_tree")),
                "description": bundle.data.pop("description", ""),
            }
        except (KeyError, ValueError) as e:
            raise BadRequest(str(e))
        # XSS handle
        self.handle_template_name_attr(pipeline_template_kwargs)

        # validate pipeline tree
        try:
            validate_web_pipeline_tree(pipeline_template_kwargs["pipeline_tree"])
            validate_pipeline_tree(pipeline_template_kwargs["pipeline_tree"], cycle_tolerate=True)
        except PipelineException as e:
            raise BadRequest(str(e))

        # Note: tastypie won't use model's create method
        try:
            pipeline_template = model.objects.create_pipeline_template(**pipeline_template_kwargs)
        except PipelineException as e:
            raise BadRequest(str(e))
        except TaskTemplate.DoesNotExist:
            raise BadRequest("flow template referred as SubProcess does not exist")
        kwargs["pipeline_template_id"] = pipeline_template.template_id
        return super(TaskTemplateResource, self).obj_create(bundle, **kwargs)

    def obj_update(self, bundle, skip_errors=False, **kwargs):
        with transaction.atomic():
            obj = bundle.obj
            try:
                pipeline_template_kwargs = {
                    "name": bundle.data.pop("name"),
                    "editor": bundle.request.user.username,
                    "pipeline_tree": json.loads(bundle.data.pop("pipeline_tree")),
                }
                if "description" in bundle.data:
                    pipeline_template_kwargs["description"] = bundle.data.pop("description")
            except (KeyError, ValueError) as e:
                raise BadRequest(str(e))
            # XSS handle
            self.handle_template_name_attr(pipeline_template_kwargs)

            # validate pipeline tree
            try:
                validate_web_pipeline_tree(pipeline_template_kwargs["pipeline_tree"])
            except PipelineException as e:
                raise BadRequest(str(e))

            try:
                obj.update_pipeline_template(**pipeline_template_kwargs)
            except PipelineException as e:
                raise BadRequest(str(e))
            bundle.data["pipeline_template"] = "/api/v3/pipeline_template/%s/" % obj.pipeline_template.pk
            return super(TaskTemplateResource, self).obj_update(bundle, **kwargs)

    def obj_delete(self, bundle, **kwargs):
        try:
            task_tmpl = TaskTemplate.objects.get(id=kwargs["pk"])
        except TaskTemplate.DoesNotExist:
            raise BadRequest("template does not exist")
        template_referencer = task_tmpl.referencer()
        if template_referencer:
            flat = ",".join(["{}:{}".format(item["id"], item["name"]) for item in template_referencer])
            raise BadRequest("flow template are referenced by other templates[%s], please delete them first" % flat)

        appmaker_referencer = task_tmpl.referencer_appmaker()
        if appmaker_referencer:
            flat = ",".join(["{}:{}".format(item["id"], item["name"]) for item in appmaker_referencer])
            raise BadRequest("flow template are referenced by mini apps[%s], please delete them first" % flat)

        result = super(TaskTemplateResource, self).obj_delete(bundle, **kwargs)
        if result:
            task_tmpl.set_deleted()
        return result

    def build_filters(self, filters=None, ignore_bad_filters=False):
        filters = super(TaskTemplateResource, self).build_filters(
            filters=filters, ignore_bad_filters=ignore_bad_filters
        )

        if "subprocess_has_update__exact" in filters:
            filters.pop("subprocess_has_update__exact")
        if "has_subprocess__exact" in filters:
            filters.pop("has_subprocess__exact")

        return filters


class TemplateSchemeResource(GCloudModelResource):
    data = fields.CharField(attribute="data", use_in="detail",)

    class Meta(GCloudModelResource.Meta):
        queryset = TemplateScheme.objects.all()
        resource_name = "scheme"
        authorization = Authorization()
        filtering = {
            "template": ALL,
        }

    def build_filters(self, filters=None, **kwargs):
        orm_filters = super(TemplateSchemeResource, self).build_filters(filters, **kwargs)
        if "project__id" in filters and "template_id" in filters:
            template_id = filters.pop("template_id")[0]
            project_id = filters.pop("project__id")[0]
            try:
                template = TaskTemplate.objects.get(pk=template_id, project_id=project_id)
            except TaskTemplate.DoesNotExist:
                message = "flow template[id={template_id}] in project[id={project_id}] does not exist".format(
                    template_id=template_id, project_id=project_id
                )
                logger.error(message)
                raise InvalidFilterError(message)
            orm_filters.update({"template__template_id": template.pipeline_template.template_id})
        elif "pk" not in filters:
            # 不允许请求全部执行方案
            orm_filters.update({"unique_id": ""})
        return orm_filters

    def obj_create(self, bundle, **kwargs):
        try:
            template_id = bundle.data.pop("template_id")
            project_id = bundle.data.pop("project__id")
            json.loads(bundle.data["data"])
        except Exception as e:
            message = "create scheme params error: %s" % e
            logger.error(message)
            raise BadRequest(message)
        try:
            template = TaskTemplate.objects.get(pk=template_id, project_id=project_id)
        except TaskTemplate.DoesNotExist:
            message = "flow template[id={template_id}] in project[id={project_id}] does not exist".format(
                template_id=template_id, project_id=project_id
            )
            logger.error(message)
            raise BadRequest(message)

        allow_or_raise_auth_failed(
            iam=iam,
            system=IAMMeta.SYSTEM_ID,
            subject=Subject("user", bundle.request.user.username),
            action=Action(IAMMeta.FLOW_EDIT_ACTION),
            resources=[
                Resource(
                    system=IAMMeta.SYSTEM_ID,
                    type=IAMMeta.FLOW_RESOURCE,
                    id=str(template.id),
                    attribute={"iam_resource_owner": template.creator},
                )
            ],
        )

        bundle.data["name"] = name_handler(bundle.data["name"], TEMPLATE_NODE_NAME_MAX_LENGTH)
        kwargs["unique_id"] = "{}-{}".format(template_id, bundle.data["name"])
        if TemplateScheme.objects.filter(unique_id=kwargs["unique_id"]).exists():
            raise BadRequest("template scheme name has existed, please change the name")
        kwargs["template"] = template.pipeline_template
        return super(TemplateSchemeResource, self).obj_create(bundle, **kwargs)

    def obj_delete(self, bundle, **kwargs):
        try:
            obj = TemplateScheme.objects.get(id=kwargs["pk"])
        except TemplateScheme.DoesNotExist:
            raise BadRequest("scheme does not exist")

        try:
            template = TaskTemplate.objects.get(pipeline_template=obj.template)
        except TaskTemplate.DoesNotExist:
            raise BadRequest("flow template the deleted scheme belongs to does not exist")

        allow_or_raise_auth_failed(
            iam=iam,
            system=IAMMeta.SYSTEM_ID,
            subject=Subject("user", bundle.request.user.username),
            action=Action(IAMMeta.FLOW_EDIT_ACTION),
            resources=[
                Resource(
                    system=IAMMeta.SYSTEM_ID,
                    type=IAMMeta.FLOW_RESOURCE,
                    id=str(template.id),
                    attribute={"iam_resource_owner": template.creator},
                )
            ],
        )
        return super(TemplateSchemeResource, self).obj_delete(bundle, **kwargs)
