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

from django.db import transaction
from django.contrib.auth import get_user_model
from tastypie import fields
from tastypie.authorization import Authorization
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from tastypie.exceptions import BadRequest, NotFound

from iam import Subject, Action
from iam.contrib.tastypie.shortcuts import allow_or_raise_immediate_response
from iam.contrib.tastypie.authorization import CompleteListIAMAuthorization


from pipeline.models import TemplateScheme

from gcloud.template_base.domains.template_manager import TemplateManager
from gcloud.template_base.apis.tastypie.resources import PipelineTemplateResource
from gcloud.common_template.models import CommonTemplate
from gcloud.commons.tastypie import GCloudModelResource, TemplateFilterPaginator
from gcloud.constants import TEMPLATE_NODE_NAME_MAX_LENGTH
from gcloud.utils.strings import standardize_name
from gcloud.iam_auth import res_factory
from gcloud.iam_auth import IAMMeta, get_iam_client
from gcloud.iam_auth.resource_helpers import SimpleResourceHelper
from gcloud.iam_auth.authorization_helpers import CommonFlowIAMAuthorizationHelper
from gcloud.contrib.operate_record.decorators import record_operation
from gcloud.contrib.operate_record.constants import RecordType, OperateType, OperateSource

iam = get_iam_client()
logger = logging.getLogger("root")


class CommonTemplateResource(GCloudModelResource):
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

    class Meta(GCloudModelResource.CommonMeta):
        queryset = CommonTemplate.objects.filter(pipeline_template__isnull=False, is_deleted=False)
        resource_name = "common_template"
        filtering = {
            "id": ALL,
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
            helper=CommonFlowIAMAuthorizationHelper(
                system=IAMMeta.SYSTEM_ID,
                create_action=IAMMeta.COMMON_FLOW_CREATE_ACTION,
                read_action=IAMMeta.COMMON_FLOW_VIEW_ACTION,
                update_action=IAMMeta.COMMON_FLOW_EDIT_ACTION,
                delete_action=IAMMeta.COMMON_FLOW_DELETE_ACTION,
            ),
        )
        iam_resource_helper = SimpleResourceHelper(
            type=IAMMeta.COMMON_FLOW_RESOURCE,
            id_field="id",
            creator_field="creator",
            name_field="name",
            iam=iam,
            system=IAMMeta.SYSTEM_ID,
            actions=[
                IAMMeta.COMMON_FLOW_VIEW_ACTION,
                IAMMeta.COMMON_FLOW_EDIT_ACTION,
                IAMMeta.COMMON_FLOW_DELETE_ACTION,
            ],
        )

    def dehydrate_pipeline_tree(self, bundle):
        return json.dumps(bundle.data["pipeline_tree"])

    def alter_list_data_to_serialize(self, request, data):
        data = super(CommonTemplateResource, self).alter_list_data_to_serialize(request, data)
        user_model = get_user_model()
        user = request.user
        collected_templates = (
            user_model.objects.get(username=user.username).tasktemplate_set.all().values_list("id", flat=True)
        )
        for bundle in data["objects"]:
            bundle.data["is_add"] = 1 if bundle.obj.id in collected_templates else 0
            notify_type = json.loads(bundle.data["notify_type"])
            bundle.data["notify_type"] = (
                notify_type if isinstance(notify_type, dict) else {"success": notify_type, "fail": notify_type}
            )
        return data

    def alter_detail_data_to_serialize(self, request, data):
        bundle = super(CommonTemplateResource, self).alter_detail_data_to_serialize(request, data)
        notify_type = json.loads(bundle.data["notify_type"])
        bundle.data["notify_type"] = (
            notify_type if isinstance(notify_type, dict) else {"success": notify_type, "fail": notify_type}
        )
        return bundle

    @record_operation(RecordType.common_template.name, OperateType.create.name, OperateSource.common.name)
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

            bundle = super(CommonTemplateResource, self).obj_create(bundle, **kwargs)

            return bundle

    @record_operation(RecordType.common_template.name, OperateType.update.name, OperateSource.common.name)
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
            return super(CommonTemplateResource, self).obj_update(bundle, **kwargs)

    @record_operation(RecordType.common_template.name, OperateType.delete.name, OperateSource.common.name)
    def obj_delete(self, bundle, **kwargs):
        try:
            template = CommonTemplate.objects.get(id=kwargs["pk"], is_deleted=False)
        except CommonTemplate.DoesNotExist:
            raise NotFound("flow template does not exist")

        manager = TemplateManager(template_model_cls=bundle.obj.__class__)
        can_delete, message = manager.can_delete(template)
        if not can_delete:
            raise BadRequest(message)

        return super(CommonTemplateResource, self).obj_delete(bundle, **kwargs)

    def build_filters(self, filters=None, ignore_bad_filters=False):
        filters = super(CommonTemplateResource, self).build_filters(
            filters=filters, ignore_bad_filters=ignore_bad_filters
        )

        if "subprocess_has_update__exact" in filters:
            filters.pop("subprocess_has_update__exact")
        if "has_subprocess__exact" in filters:
            filters.pop("has_subprocess__exact")

        return filters


class CommonTemplateSchemeResource(GCloudModelResource):
    data = fields.CharField(attribute="data", use_in="detail",)

    class Meta(GCloudModelResource.CommonMeta):
        queryset = TemplateScheme.objects.all()
        resource_name = "common_scheme"
        authorization = Authorization()
        filtering = {
            "template": ALL,
        }
        limit = 0

    def build_filters(self, filters=None, **kwargs):
        orm_filters = super(CommonTemplateSchemeResource, self).build_filters(filters, **kwargs)
        if "project__id" in filters and "template_id" in filters:
            template_id = filters.pop("template_id")[0]
            project__id = filters.pop("project__id")[0]
            template = CommonTemplate.objects.get(pk=template_id)
            orm_filters.update(
                {
                    "template__template_id": template.pipeline_template.template_id,
                    # 这里通过项目ID前缀隔离不同业务在同一个公共流程下的执行方案
                    "unique_id__startswith": "%s-" % project__id,
                }
            )
        elif "pk" not in filters:
            # 不允许请求全部执行方案
            orm_filters.update({"unique_id": ""})
        return orm_filters

    def obj_create(self, bundle, **kwargs):
        try:
            project_id = bundle.data.pop("project__id")
            template_id = bundle.data.pop("template_id")
            common_template = CommonTemplate.objects.get(pk=template_id)
        except Exception:
            raise BadRequest("common template does not exist")

        allow_or_raise_immediate_response(
            iam=iam,
            system=IAMMeta.SYSTEM_ID,
            subject=Subject("user", bundle.request.user.username),
            action=Action(IAMMeta.COMMON_FLOW_EDIT_ACTION),
            resources=res_factory.resources_for_common_flow_obj(common_template),
        )

        bundle.data["name"] = standardize_name(bundle.data["name"], TEMPLATE_NODE_NAME_MAX_LENGTH)
        kwargs["unique_id"] = "%s-%s-%s" % (project_id, template_id, bundle.data["name"])
        if TemplateScheme.objects.filter(unique_id=kwargs["unique_id"]).exists():
            raise BadRequest("common template scheme name has existed, please change the name")
        kwargs["template"] = common_template.pipeline_template
        return super(CommonTemplateSchemeResource, self).obj_create(bundle, **kwargs)

    def obj_delete(self, bundle, **kwargs):
        try:
            scheme_id = kwargs["pk"]
            scheme = TemplateScheme.objects.get(pk=scheme_id)
            common_template = CommonTemplate.objects.get(pipeline_template=scheme.template)
        except Exception:
            raise BadRequest("common scheme or template does not exist")

        allow_or_raise_immediate_response(
            iam=iam,
            system=IAMMeta.SYSTEM_ID,
            subject=Subject("user", bundle.request.user.username),
            action=Action(IAMMeta.COMMON_FLOW_EDIT_ACTION),
            resources=res_factory.resources_for_common_flow_obj(common_template),
        )

        return super(CommonTemplateSchemeResource, self).obj_delete(bundle, **kwargs)
