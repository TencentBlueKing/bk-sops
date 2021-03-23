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

from gcloud.label.models import TemplateLabelRelation, Label
from pipeline.exceptions import PipelineException
from pipeline.models import TemplateScheme
from pipeline.validators.base import validate_pipeline_tree
from pipeline_web.parser.validator import validate_web_pipeline_tree

from iam import Subject, Action
from iam.contrib.tastypie.shortcuts import allow_or_raise_immediate_response
from iam.contrib.tastypie.authorization import CompleteListIAMAuthorization

from gcloud.commons.template.resources import PipelineTemplateResource
from gcloud.core.constant import TEMPLATE_NODE_NAME_MAX_LENGTH
from gcloud.utils.strings import name_handler, pipeline_node_name_handle
from gcloud.tasktmpl3.models import TaskTemplate
from gcloud.commons.tastypie import GCloudModelResource, TemplateFilterPaginator
from gcloud.core.resources import ProjectResource
from gcloud.iam_auth import res_factory
from gcloud.iam_auth import IAMMeta, get_iam_client
from gcloud.iam_auth.resource_helpers import FlowResourceHelper
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
    description = fields.CharField(attribute="pipeline_template__description", readonly=True, null=True)

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
        ordering = ["pipeline_template"]
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
        iam_resource_helper = FlowResourceHelper(
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
        template_ids = [bundle.obj.id for bundle in data["objects"]]
        templates_labels = TemplateLabelRelation.objects.fetch_templates_labels(template_ids)
        for bundle in data["objects"]:
            if bundle.obj.id in collected_templates:
                bundle.data["is_add"] = 1
            else:
                bundle.data["is_add"] = 0
            bundle.data["template_labels"] = templates_labels.get(bundle.obj.id, [])

        return data

    def alter_detail_data_to_serialize(self, request, data):
        bundle = super(TaskTemplateResource, self).alter_detail_data_to_serialize(request, data)
        template_id = bundle.obj.id
        labels = TemplateLabelRelation.objects.fetch_templates_labels([template_id]).get(template_id, [])
        bundle.data["template_labels"] = [label["label_id"] for label in labels]
        return bundle

    def obj_create(self, bundle, **kwargs):
        label_ids = bundle.data.get("template_labels")
        if label_ids and len(label_ids) > 0 and bundle.obj:
            label_ids = list(set(label_ids))
            if not Label.objects.check_label_ids(label_ids):
                raise BadRequest("Containing template label not exist, please check.")

        with transaction.atomic():
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

            bundle = super(TaskTemplateResource, self).obj_create(bundle, **kwargs)
            if isinstance(label_ids, list) and len(label_ids) > 0:
                try:
                    TemplateLabelRelation.objects.set_labels_for_template(bundle.obj.id, label_ids)
                except Exception as e:
                    raise BadRequest(str(e))

            return bundle

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

            label_ids = bundle.data.get("template_labels")
            if label_ids is not None and len(label_ids) > 0:
                label_ids = list(set(label_ids))
                if not Label.objects.check_label_ids(label_ids):
                    raise BadRequest("Containing template label not exist, please check.")
                try:
                    TemplateLabelRelation.objects.set_labels_for_template(obj.id, label_ids)
                except Exception as e:
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
        label_ids = filters.get("label_ids")

        filters = super(TaskTemplateResource, self).build_filters(
            filters=filters, ignore_bad_filters=ignore_bad_filters
        )

        if label_ids:
            label_ids = [int(label_id) for label_id in label_ids.strip().split(",")]
            template_ids = list(TemplateLabelRelation.objects.fetch_template_ids_using_union_labels(label_ids))
            filters.update({"id__in": template_ids})
        if "subprocess_has_update__exact" in filters:
            filters.pop("subprocess_has_update__exact")
        if "has_subprocess__exact" in filters:
            filters.pop("has_subprocess__exact")

        return filters


class TemplateSchemeResource(GCloudModelResource):
    data = fields.CharField(attribute="data", use_in="detail")

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
            except Exception as e:
                message = "Error on getting template[id={template_id}] in project[id={project_id}]: {error}".format(
                    template_id=template_id, project_id=project_id, error=e
                )
                logger.error(message)
                raise InvalidFilterError(message)
            orm_filters.update({"template__template_id": template.pipeline_template.template_id})
        elif "pk" not in filters:
            # 不允许请求全部执行方案
            orm_filters.update({"unique_id": ""})
        return orm_filters

    def obj_get_list(self, bundle, **kwargs):
        template_id = bundle.request.GET.get("template_id")
        project_id = bundle.request.GET.get("project__id")
        if template_id is None or project_id is None:
            message = "scheme params error: need template_id and project__id"
            logger.error(message)
            raise BadRequest(message)
        self._check_user_scheme_permission(bundle.request.user.username, template_id, project_id)
        return super(TemplateSchemeResource, self).obj_get_list(bundle, **kwargs)

    def obj_get(self, bundle, **kwargs):
        obj = super(TemplateSchemeResource, self).obj_get(bundle, **kwargs)
        template_id = obj.unique_id.split("-")[0]
        self._check_user_scheme_permission(bundle.request.user.username, template_id)
        return obj

    def obj_create(self, bundle, **kwargs):
        try:
            template_id = bundle.data.pop("template_id")
            project_id = bundle.data.pop("project__id")
            json.loads(bundle.data["data"])
        except Exception as e:
            message = "create scheme params error: %s" % e
            logger.error(message)
            raise BadRequest(message)
        _, template = self._check_user_scheme_permission(bundle.request.user.username, template_id, project_id)

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
        template_id = obj.unique_id.split("-")[0]
        self._check_user_scheme_permission(bundle.request.user.username, template_id)
        return super(TemplateSchemeResource, self).obj_delete(bundle, **kwargs)

    @staticmethod
    def _check_user_scheme_permission(username, template_id, project_id=None):
        if project_id is None:
            try:
                template = TaskTemplate.objects.get(pk=template_id)
            except TaskTemplate.DoesNotExist:
                message = "flow template[id={template_id}] does not exist".format(template_id=template_id)
                logger.error(message)
                raise BadRequest(message)
        else:
            try:
                template = TaskTemplate.objects.get(pk=template_id, project_id=project_id)
            except TaskTemplate.DoesNotExist:
                message = "flow template[id={template_id}] in project[id={project_id}] does not exist".format(
                    template_id=template_id, project_id=project_id
                )
                logger.error(message)
                raise BadRequest(message)
        allow_or_raise_immediate_response(
            iam=iam,
            system=IAMMeta.SYSTEM_ID,
            subject=Subject("user", username),
            action=Action(IAMMeta.FLOW_EDIT_ACTION),
            resources=res_factory.resources_for_flow_obj(template),
        )
        return True, template
