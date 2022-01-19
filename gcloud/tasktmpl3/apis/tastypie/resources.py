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

import ujson as json
from django.contrib.auth import get_user_model
from django.db import transaction
from tastypie import fields
from tastypie.authorization import Authorization
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from tastypie.exceptions import BadRequest, InvalidFilterError

from gcloud.iam_auth.utils import check_project_or_admin_view_action_for_user
from gcloud.label.models import TemplateLabelRelation, Label
from pipeline.models import TemplateScheme, TemplateRelationship

from iam import Subject, Action
from iam.contrib.tastypie.shortcuts import allow_or_raise_immediate_response
from iam.contrib.tastypie.authorization import CompleteListIAMAuthorization

from gcloud.utils.strings import standardize_name
from gcloud.constants import TEMPLATE_NODE_NAME_MAX_LENGTH
from gcloud.tasktmpl3.models import TaskTemplate
from gcloud.template_base.domains.template_manager import TemplateManager
from gcloud.template_base.apis.tastypie.resources import PipelineTemplateResource
from gcloud.commons.tastypie import GCloudModelResource, TemplateFilterPaginator
from gcloud.core.resources import ProjectResource
from gcloud.iam_auth import res_factory
from gcloud.iam_auth import IAMMeta, get_iam_client
from gcloud.iam_auth.resource_helpers import FlowResourceHelper
from gcloud.iam_auth.authorization_helpers import FlowIAMAuthorizationHelper
from gcloud.contrib.operate_record.decorators import record_operation
from gcloud.contrib.operate_record.constants import RecordType, OperateType, OperateSource
from gcloud.user_custom_config.constants import TASKTMPL_ORDERBY_OPTIONS

logger = logging.getLogger("root")
iam = get_iam_client()


class ProjectBasedTaskTemplateIAMAuthorization(CompleteListIAMAuthorization):
    def read_list(self, object_list, bundle):
        project_id = bundle.request.GET.get("project__id")
        check_project_or_admin_view_action_for_user(project_id, bundle.request.user.username)
        return object_list


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

    extra_ordering = {"edit_time", "create_time"}

    class Meta(GCloudModelResource.CommonMeta):
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
        ordering = [
            "pipeline_template",
        ] + [order["value"] for order in TASKTMPL_ORDERBY_OPTIONS]
        q_fields = ["id", "pipeline_template__name"]
        paginator_class = TemplateFilterPaginator
        # iam config
        authorization = ProjectBasedTaskTemplateIAMAuthorization(
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
                IAMMeta.FLOW_CREATE_CLOCKED_TASK_ACTION,
            ],
        )

    def apply_sorting(self, obj_list, options=None):
        if not options:
            return super().apply_sorting(obj_list, options=options)
        options = options.copy()
        order_by = options.get("order_by", "")
        prefix = "pipeline_template__"
        if order_by.startswith("-"):
            prefix = "-" + prefix
        if order_by.lstrip("-") in self.__class__.extra_ordering:
            order_by = prefix + order_by.lstrip("-")
            options["order_by"] = order_by
        return super().apply_sorting(obj_list, options=options)

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
            bundle.data["is_add"] = 1 if bundle.obj.id in collected_templates else 0
            bundle.data["template_labels"] = templates_labels.get(bundle.obj.id, [])
            notify_type = json.loads(bundle.data["notify_type"])
            bundle.data["notify_type"] = (
                notify_type if isinstance(notify_type, dict) else {"success": notify_type, "fail": notify_type}
            )
        return data

    def alter_detail_data_to_serialize(self, request, data):
        bundle = super(TaskTemplateResource, self).alter_detail_data_to_serialize(request, data)
        template_id = bundle.obj.id
        labels = TemplateLabelRelation.objects.fetch_templates_labels([template_id]).get(template_id, [])
        bundle.data["template_labels"] = [label["label_id"] for label in labels]
        notify_type = json.loads(bundle.data["notify_type"])
        bundle.data["notify_type"] = (
            notify_type if isinstance(notify_type, dict) else {"success": notify_type, "fail": notify_type}
        )
        return bundle

    @record_operation(RecordType.template.name, OperateType.create.name, OperateSource.project.name)
    def obj_create(self, bundle, **kwargs):
        manager = TemplateManager(template_model_cls=bundle.obj.__class__)
        try:
            name = bundle.data.pop("name")
            creator = bundle.request.user.username
            pipeline_tree = json.loads(bundle.data.pop("pipeline_tree"))
            description = bundle.data.pop("description", "")
            notify_type = bundle.data.get("notify_type") or {"success": [], "fail": []}
            if isinstance(notify_type, str):
                loaded_notify_type = json.loads(notify_type)
                notify_type = {"success": loaded_notify_type, "fail": loaded_notify_type}
            bundle.data["notify_type"] = json.dumps(notify_type)
        except (KeyError, ValueError) as e:
            raise BadRequest(str(e))

        with transaction.atomic():
            result = manager.create_pipeline(
                name=name, creator=creator, pipeline_tree=pipeline_tree, description=description
            )

            if not result["result"]:
                logger.error(result["verbose_message"])
                raise BadRequest(result["verbose_message"])

            kwargs["pipeline_template_id"] = result["data"].template_id

            bundle = super(TaskTemplateResource, self).obj_create(bundle, **kwargs)
            self._sync_template_labels(bundle)

            return bundle

    @record_operation(RecordType.template.name, OperateType.update.name, OperateSource.project.name)
    def obj_update(self, bundle, skip_errors=False, **kwargs):
        template = bundle.obj
        manager = TemplateManager(template_model_cls=bundle.obj.__class__)

        try:
            name = bundle.data.pop("name")
            editor = bundle.request.user.username
            pipeline_tree = json.loads(bundle.data.pop("pipeline_tree"))
            description = bundle.data.pop("description")
            notify_type = bundle.data.get("notify_type") or {"success": [], "fail": []}
            if isinstance(notify_type, str):
                loaded_notify_type = json.loads(notify_type)
                notify_type = {"success": loaded_notify_type, "fail": loaded_notify_type}
            bundle.data["notify_type"] = json.dumps(notify_type)
        except (KeyError, ValueError) as e:
            raise BadRequest(str(e))

        with transaction.atomic():
            result = manager.update_pipeline(
                pipeline_template=template.pipeline_template,
                editor=editor,
                name=name,
                pipeline_tree=pipeline_tree,
                description=description,
            )

            if not result["result"]:
                logger.error(result["verbose_message"])
                raise BadRequest(result["verbose_message"])
            bundle.data["pipeline_template"] = "/api/v3/pipeline_template/%s/" % template.pipeline_template.pk

            self._sync_template_labels(bundle)

            return super(TaskTemplateResource, self).obj_update(bundle, **kwargs)

    @record_operation(RecordType.template.name, OperateType.delete.name, OperateSource.project.name)
    def obj_delete(self, bundle, **kwargs):
        try:
            template = TaskTemplate.objects.get(id=kwargs["pk"])
        except TaskTemplate.DoesNotExist:
            raise BadRequest("template does not exist")

        manager = TemplateManager(template_model_cls=bundle.obj.__class__)
        can_delete, message = manager.can_delete(template)
        if not can_delete:
            raise BadRequest(message)

        # 删除该流程引用的子流程节点的执行方案
        pipeline_template_id = template.pipeline_template.template_id
        relation_queryset = TemplateRelationship.objects.filter(ancestor_template_id=pipeline_template_id)
        for relation in relation_queryset:
            relation.templatescheme_set.clear()

        return super(TaskTemplateResource, self).obj_delete(bundle, **kwargs)

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

    @staticmethod
    def _sync_template_labels(bundle):
        """
        创建或更新模版时同步模版标签数据
        """
        label_ids = bundle.data.get("template_labels")
        if label_ids is not None:
            label_ids = list(set(label_ids))
            if not Label.objects.check_label_ids(label_ids):
                raise BadRequest("Containing template label not exist, please check.")
            try:
                TemplateLabelRelation.objects.set_labels_for_template(bundle.obj.id, label_ids)
            except Exception as e:
                raise BadRequest(str(e))


class TemplateSchemeResource(GCloudModelResource):
    data = fields.CharField(attribute="data", use_in="detail")

    class Meta(GCloudModelResource.CommonMeta):
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

        bundle.data["name"] = standardize_name(bundle.data["name"], TEMPLATE_NODE_NAME_MAX_LENGTH)
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
