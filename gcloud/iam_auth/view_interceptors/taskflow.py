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

import abc

import ujson as json

from gcloud.constants import NON_COMMON_TEMPLATE_TYPES, PROJECT
from gcloud.iam_auth import IAMMeta, PermissionCheck, PermissionService, get_iam_client, res_factory
from gcloud.iam_auth.creator import get_task_creator_ids, is_flow_creator, is_task_creator
from gcloud.iam_auth.exceptions import AuthFailedException, IAMPermissionDenied, IAMResourceNotFound
from gcloud.iam_auth.intercept import ViewInterceptor
from gcloud.iam_auth.models import Action, Request, Subject
from gcloud.iam_auth.shortcuts import allow_or_raise_auth_failed


class TaskSingleActionInterceptor(ViewInterceptor, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get_task_id(self, request, *args, **kwargs):
        raise NotImplementedError()

    def process(self, request, *args, **kwargs):
        task_id = self.get_task_id(request, *args, **kwargs)
        tenant_id = request.user.tenant_id
        if is_task_creator(request.user.username, tenant_id, task_id):
            return
        iam = get_iam_client(tenant_id)
        subject = Subject("user", request.user.username)
        action = Action(self.action)
        resources = res_factory.resources_for_task(task_id, tenant_id)

        request = Request(IAMMeta.SYSTEM_ID, subject, action, resources, {})
        allowed = iam.is_allowed_with_cache(request)

        if not allowed:
            raise AuthFailedException(IAMMeta.SYSTEM_ID, subject, action, resources)


class TaskSingleActionPostInterceptor(TaskSingleActionInterceptor):
    def get_task_id(self, request, *args, **kwargs):
        return json.loads(request.body)["instance_id"]


class TaskSingleActionGetInterceptor(TaskSingleActionInterceptor):
    def get_task_id(self, request, *args, **kwargs):
        return request.GET["instance_id"]


class DataViewInterceptor(TaskSingleActionGetInterceptor):
    action = IAMMeta.TASK_VIEW_ACTION


class DetailViewInterceptor(TaskSingleActionGetInterceptor):
    action = IAMMeta.TASK_VIEW_ACTION


class TaskActionInterceptor(TaskSingleActionPostInterceptor):
    action = IAMMeta.TASK_OPERATE_ACTION


class NodesActionInterceptor(TaskSingleActionPostInterceptor):
    action = IAMMeta.TASK_OPERATE_ACTION


class NodeActionV2Inpterceptor(TaskSingleActionPostInterceptor):
    action = IAMMeta.TASK_OPERATE_ACTION

    def get_task_id(self, request, *args, **kwargs):
        return kwargs["task_id"]


class SpecNodesTimerResetInpterceptor(TaskSingleActionPostInterceptor):
    action = IAMMeta.TASK_OPERATE_ACTION


class TaskCloneInpterceptor(TaskSingleActionPostInterceptor):
    action = IAMMeta.TASK_CLONE_ACTION


class TaskFuncClaimInterceptor(TaskSingleActionPostInterceptor):
    action = IAMMeta.TASK_CLAIM_ACTION


class GetNodeLogInterceptor(TaskSingleActionGetInterceptor):
    action = IAMMeta.TASK_VIEW_ACTION


class StatusViewInterceptor(TaskSingleActionGetInterceptor):
    action = IAMMeta.TASK_VIEW_ACTION


class BatchStatusViewInterceptor(ViewInterceptor):
    def process(self, request, *args, **kwargs):
        task_ids = json.loads(request.body).get("task_ids") or []
        tenant_id = request.user.tenant_id
        resources_list = res_factory.resources_list_for_tasks(task_ids, tenant_id)
        resources = [item[0] for item in resources_list]
        requested_ids = {str(task_id) for task_id in task_ids}
        resolved_ids = {str(resource.id) for resource in resources}
        if requested_ids != resolved_ids:
            missing_id = next(iter(requested_ids - resolved_ids), "unknown")
            raise IAMResourceNotFound(IAMMeta.TASK_RESOURCE, missing_id)
        creator_ids = get_task_creator_ids(request.user.username, tenant_id, task_ids)
        resources = [resource for resource in resources if str(resource.id) not in creator_ids]
        if not resources:
            return
        decisions = PermissionService().allowed_resources(
            request.user.username, tenant_id, IAMMeta.TASK_VIEW_ACTION, resources
        )
        missing = [
            PermissionCheck(IAMMeta.TASK_VIEW_ACTION, resource)
            for resource in resources
            if not decisions[str(resource.id)]
        ]
        if missing:
            raise IAMPermissionDenied(missing)


class PreviewTaskTreeInterceptor(ViewInterceptor):
    """
    preview_task_tree 接口模板级 IAM 鉴权：
    - template_source 为项目流程时，校验 FLOW_VIEW_ACTION
    - template_source 为公共流程时，校验 COMMON_FLOW_VIEW_ACTION
    """

    def process(self, request, *args, **kwargs):
        tenant_id = request.user.tenant_id
        params = json.loads(request.body)
        template_source = params.get("template_source", PROJECT)
        template_id = params.get("template_id")

        if template_source in NON_COMMON_TEMPLATE_TYPES and is_flow_creator(
            request.user.username,
            tenant_id,
            template_id,
            project_id=kwargs.get("project_id"),
        ):
            return

        iam = get_iam_client(tenant_id)
        subject = Subject("user", request.user.username)

        if template_source in NON_COMMON_TEMPLATE_TYPES:
            action = Action(IAMMeta.FLOW_VIEW_ACTION)
            resources = res_factory.resources_for_flow(template_id, tenant_id)
        else:
            action = Action(IAMMeta.COMMON_FLOW_VIEW_ACTION)
            resources = res_factory.resources_for_common_flow(template_id, tenant_id)

        allow_or_raise_auth_failed(iam, IAMMeta.SYSTEM_ID, subject, action, resources, cache=True)
