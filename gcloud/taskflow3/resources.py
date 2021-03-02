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
from django.utils.translation import ugettext_lazy as _
from django.db.models import Q
from tastypie import fields
from tastypie.authorization import ReadOnlyAuthorization
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from tastypie.exceptions import BadRequest, NotFound

from iam import Subject, Action, Request
from iam.contrib.tastypie.shortcuts import allow_or_raise_immediate_response
from iam.contrib.tastypie.authorization import CustomCreateCompleteListIAMAuthorization

from pipeline.engine import states
from pipeline.exceptions import PipelineException
from pipeline.models import PipelineInstance
from pipeline_web.parser.validator import validate_web_pipeline_tree

from gcloud.utils.strings import name_handler, pipeline_node_name_handle
from gcloud.core.constant import TASK_NAME_MAX_LENGTH
from gcloud.commons.template.models import CommonTemplate
from gcloud.commons.tastypie import GCloudModelResource
from gcloud.tasktmpl3.models import TaskTemplate
from gcloud.taskflow3.models import TaskFlowInstance
from gcloud.taskflow3.constants import PROJECT
from gcloud.core.resources import ProjectResource
from gcloud.contrib.appmaker.models import AppMaker
from gcloud.iam_auth import res_factory
from gcloud.iam_auth import IAMMeta, get_iam_client
from gcloud.iam_auth.resource_helpers import TaskResourceHelper
from gcloud.iam_auth.authorization_helpers import TaskIAMAuthorizationHelper
from gcloud.iam_auth.utils import get_flow_allowed_actions_for_user, get_common_flow_allowed_actions_for_user

logger = logging.getLogger("root")
iam = get_iam_client()


class PipelineInstanceResource(GCloudModelResource):
    class Meta(GCloudModelResource.Meta):
        queryset = PipelineInstance.objects.filter(is_deleted=False)
        resource_name = "pipeline_instance"
        authorization = ReadOnlyAuthorization()
        filtering = {
            "name": ALL,
            "is_finished": ALL,
            "is_revoked": ALL,
            "creator": ALL,
            "category": ALL,
            "subprocess_has_update": ALL,
            "edit_time": ["gte", "lte"],
            "executor": ALL,
            "is_started": ALL,
            "start_time": ["gte", "lte"],
        }


class TaskFlowInstanceResource(GCloudModelResource):
    project = fields.ForeignKey(ProjectResource, "project", full=True)
    pipeline_instance = fields.ForeignKey(PipelineInstanceResource, "pipeline_instance")
    name = fields.CharField(attribute="name", readonly=True, null=True)
    instance_id = fields.IntegerField(attribute="instance_id", readonly=True)
    category_name = fields.CharField(attribute="category_name", readonly=True)
    create_time = fields.DateTimeField(attribute="create_time", readonly=True, null=True)
    start_time = fields.DateTimeField(attribute="start_time", readonly=True, null=True)
    finish_time = fields.DateTimeField(attribute="finish_time", readonly=True, null=True)
    elapsed_time = fields.IntegerField(attribute="elapsed_time", readonly=True)
    is_started = fields.BooleanField(attribute="is_started", readonly=True, null=True)
    is_finished = fields.BooleanField(attribute="is_finished", readonly=True, null=True)
    is_revoked = fields.BooleanField(attribute="is_revoked", readonly=True, null=True)
    is_expired = fields.BooleanField(attribute="is_expired", readonly=True, null=True)
    creator_name = fields.CharField(attribute="creator_name", readonly=True, null=True)
    executor_name = fields.CharField(attribute="executor_name", readonly=True, null=True)
    pipeline_tree = fields.DictField(attribute="pipeline_tree", use_in="detail", readonly=True, null=True)
    subprocess_info = fields.DictField(attribute="subprocess_info", use_in="detail", readonly=True)

    class Meta(GCloudModelResource.Meta):
        queryset = TaskFlowInstance.objects.filter(pipeline_instance__isnull=False, is_deleted=False)
        resource_name = "taskflow"
        filtering = {
            "id": ALL,
            "project": ALL_WITH_RELATIONS,
            "name": ALL,
            "category": ALL,
            "create_method": ALL,
            "create_info": ALL,
            "template_source": ALL,
            "template_id": ALL,
            "pipeline_instance": ALL_WITH_RELATIONS,
        }
        ordering = ["pipeline_instance"]
        q_fields = ["id", "pipeline_instance__name"]
        creator_or_executor_fields = ["pipeline_instance__creator", "pipeline_instance__executor"]
        # iam config
        authorization = CustomCreateCompleteListIAMAuthorization(
            iam=iam,
            helper=TaskIAMAuthorizationHelper(
                system=IAMMeta.SYSTEM_ID,
                create_action=None,
                read_action=IAMMeta.TASK_VIEW_ACTION,
                update_action=IAMMeta.TASK_EDIT_ACTION,
                delete_action=IAMMeta.TASK_DELETE_ACTION,
            ),
        )
        iam_resource_helper = TaskResourceHelper(
            iam=iam,
            system=IAMMeta.SYSTEM_ID,
            actions=[
                IAMMeta.TASK_VIEW_ACTION,
                IAMMeta.TASK_EDIT_ACTION,
                IAMMeta.TASK_OPERATE_ACTION,
                IAMMeta.TASK_CLAIM_ACTION,
                IAMMeta.TASK_DELETE_ACTION,
                IAMMeta.TASK_CLONE_ACTION,
            ],
        )

    def alter_list_data_to_serialize(self, request, data):
        data = super().alter_list_data_to_serialize(request, data)

        # 项目流程任务
        templates_id = {
            bundle.obj.template_id
            for bundle in data["objects"]
            if bundle.obj.template_id and bundle.obj.template_source == "project"
        }
        templates_allowed_actions = get_flow_allowed_actions_for_user(
            request.user.username, [IAMMeta.FLOW_VIEW_ACTION, IAMMeta.FLOW_CREATE_TASK_ACTION], templates_id
        )
        template_info = TaskTemplate.objects.filter(id__in=templates_id).values(
            "id", "pipeline_template__name", "is_deleted"
        )
        template_info_map = {
            str(t["id"]): {"name": t["pipeline_template__name"], "is_deleted": t["is_deleted"]} for t in template_info
        }

        # 公共流程任务
        common_templates_id = {
            bundle.obj.template_id
            for bundle in data["objects"]
            if bundle.obj.template_id and bundle.obj.template_source == "common"
        }
        common_templates_allowed_actions = get_common_flow_allowed_actions_for_user(
            request.user.username, [IAMMeta.COMMON_FLOW_VIEW_ACTION], common_templates_id,
        )
        common_template_info = CommonTemplate.objects.filter(id__in=common_templates_id).values(
            "id", "pipeline_template__name", "is_deleted"
        )
        common_template_info_map = {
            str(t["id"]): {"name": t["pipeline_template__name"], "is_deleted": t["is_deleted"]}
            for t in common_template_info
        }

        for bundle in data["objects"]:
            if bundle.obj.template_source == "project":
                bundle.data["template_name"] = template_info_map.get(bundle.obj.template_id, {}).get("name")
                bundle.data["template_deleted"] = template_info_map.get(bundle.obj.template_id, {}).get(
                    "is_deleted", True
                )
                for act, allowed in templates_allowed_actions.get(str(bundle.obj.template_id), {}).items():
                    if allowed:
                        bundle.data["auth_actions"].append(act)
            elif bundle.obj.template_source == "common":
                bundle.data["template_name"] = common_template_info_map.get(bundle.obj.template_id, {}).get("name")
                bundle.data["template_deleted"] = common_template_info_map.get(bundle.obj.template_id, {}).get(
                    "is_deleted", True
                )
                for act, allowed in common_templates_allowed_actions.get(str(bundle.obj.template_id), {}).items():
                    if allowed:
                        bundle.data["auth_actions"].append(act)
                action = IAMMeta.COMMON_FLOW_CREATE_TASK_ACTION
                action_request = Request(
                    system=IAMMeta.SYSTEM_ID,
                    subject=Subject("user", request.user.username),
                    action=Action(action),
                    resources=[
                        res_factory.resources_for_project_obj(bundle.obj.project)[0],
                        res_factory.resources_for_common_flow(bundle.obj.template_id)[0],
                    ],
                    environment=None,
                )
                allowed = iam.is_allowed(action_request)
                if allowed:
                    bundle.data["auth_actions"].append(action)

        return data

    def build_filters(self, filters=None, ignore_bad_filters=False):
        if filters is None:
            filters = {}

        orm_filters = super(GCloudModelResource, self).build_filters(filters, ignore_bad_filters)
        if filters.get("creator_or_executor", "").strip():
            if getattr(self.Meta, "creator_or_executor_fields", []):
                queries = [
                    Q(**{"%s" % field: filters["creator_or_executor"]})
                    for field in self.Meta.creator_or_executor_fields
                ]
                query = queries.pop()
                for item in queries:
                    query |= item
                if "q" in orm_filters:
                    orm_filters["q"] |= query
                else:
                    orm_filters["q"] = query
        return orm_filters

    @staticmethod
    def handle_task_name_attr(data):
        data["name"] = name_handler(data["name"], TASK_NAME_MAX_LENGTH)
        pipeline_node_name_handle(data["pipeline_tree"])

    def dehydrate_pipeline_tree(self, bundle):
        return json.dumps(bundle.data["pipeline_tree"])

    def obj_create(self, bundle, **kwargs):
        model = bundle.obj.__class__
        try:
            template_id = bundle.data["template_id"]
            template_source = bundle.data.get("template_source", PROJECT)
            creator = bundle.request.user.username
            pipeline_instance_kwargs = {
                "name": bundle.data.pop("name"),
                "creator": creator,
                "pipeline_tree": json.loads(bundle.data.pop("pipeline_tree")),
            }
            if "description" in bundle.data:
                pipeline_instance_kwargs["description"] = bundle.data.pop("description")
        except (KeyError, ValueError) as e:
            raise BadRequest(str(e))

        try:
            project = ProjectResource().get_via_uri(bundle.data.get("project"), request=bundle.request)
        except NotFound:
            raise BadRequest("project with uri(%s) does not exist" % bundle.data.get("project"))

        # perms validate
        if template_source == PROJECT:
            try:
                template = TaskTemplate.objects.get(pk=template_id, project=project, is_deleted=False)
            except TaskTemplate.DoesNotExist:
                raise BadRequest("template[pk=%s] does not exist" % template_id)

            create_method = bundle.data["create_method"]

            # mini app create task perm
            if create_method == "app_maker":
                app_maker_id = bundle.data["create_info"]
                try:
                    app_maker = AppMaker.objects.get(id=app_maker_id)
                except AppMaker.DoesNotExist:
                    raise BadRequest("app_maker[pk=%s] does not exist" % app_maker_id)

                allow_or_raise_immediate_response(
                    iam=iam,
                    system=IAMMeta.SYSTEM_ID,
                    subject=Subject("user", bundle.request.user.username),
                    action=Action(IAMMeta.MINI_APP_CREATE_TASK_ACTION),
                    resources=res_factory.resources_for_mini_app_obj(app_maker),
                )

            # flow create task perm
            else:
                allow_or_raise_immediate_response(
                    iam=iam,
                    system=IAMMeta.SYSTEM_ID,
                    subject=Subject("user", bundle.request.user.username),
                    action=Action(IAMMeta.FLOW_CREATE_TASK_ACTION),
                    resources=res_factory.resources_for_flow_obj(template),
                )

        else:
            try:
                template = CommonTemplate.objects.get(pk=template_id, is_deleted=False)
            except CommonTemplate.DoesNotExist:
                raise BadRequest("common template[pk=%s] does not exist" % template_id)

            allow_or_raise_immediate_response(
                iam=iam,
                system=IAMMeta.SYSTEM_ID,
                subject=Subject("user", bundle.request.user.username),
                action=Action(IAMMeta.COMMON_FLOW_CREATE_TASK_ACTION),
                resources=[
                    res_factory.resources_for_project_obj(project)[0],
                    res_factory.resources_for_common_flow_obj(template)[0],
                ],
            )

        # XSS handle
        self.handle_task_name_attr(pipeline_instance_kwargs)

        # validate pipeline tree
        try:
            validate_web_pipeline_tree(pipeline_instance_kwargs["pipeline_tree"])
        except PipelineException as e:
            raise BadRequest(str(e))

        try:
            pipeline_instance = model.objects.create_pipeline_instance(template, **pipeline_instance_kwargs)
        except PipelineException as e:
            raise BadRequest(str(e))
        kwargs["category"] = template.category
        if bundle.data["flow_type"] == "common_func":
            kwargs["current_flow"] = "func_claim"
        else:
            kwargs["current_flow"] = "execute_task"
        kwargs["pipeline_instance_id"] = pipeline_instance.id
        super(TaskFlowInstanceResource, self).obj_create(bundle, **kwargs)
        return bundle

    def obj_delete(self, bundle, **kwargs):
        try:
            taskflow = TaskFlowInstance.objects.get(id=kwargs["pk"])
        except Exception:
            raise BadRequest("taskflow does not exits")

        raw_state = taskflow.raw_state

        if raw_state and raw_state not in states.ARCHIVED_STATES:
            raise BadRequest(_("无法删除未进入完成或撤销状态的流程"))

        return super(TaskFlowInstanceResource, self).obj_delete(bundle, **kwargs)
