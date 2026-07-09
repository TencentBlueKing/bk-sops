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

import ujson as json
from iam import Action, Request, Subject
from iam.exceptions import AuthFailedException, MultiAuthFailedException

from gcloud.core.models import Project
from gcloud.iam_auth import IAMMeta, get_iam_client, res_factory
from gcloud.iam_auth.intercept import ViewInterceptor
from gcloud.tasktmpl3.models import TaskTemplate
from gcloud.template_base.utils import read_template_data_file
from gcloud.utils.strings import string_to_boolean


class TaskTemplateViewInterceptor(ViewInterceptor):
    def process(self, request, *args, **kwargs):
        template_id = request.GET.get("template_id")
        tenant_id = request.user.tenant_id
        subject = Subject("user", request.user.username)
        action = Action(IAMMeta.FLOW_VIEW_ACTION)
        resources = res_factory.resources_for_flow(template_id, tenant_id)
        request = Request(IAMMeta.SYSTEM_ID, subject, action, resources, {})
        iam = get_iam_client(tenant_id)
        allowed = iam.is_allowed(request)

        if not allowed:
            raise AuthFailedException(IAMMeta.SYSTEM_ID, subject, action, resources)


class FormInterceptor(TaskTemplateViewInterceptor):
    pass


class ParentsInterceptor(TaskTemplateViewInterceptor):
    pass


class FetchPipelineTreeInterceptor(TaskTemplateViewInterceptor):
    pass


class BatchFormInterceptor(ViewInterceptor):
    def process(self, request, *args, **kwargs):
        data = request.data
        template_list = data["templates"]
        tenant_id = request.user.tenant_id
        subject = Subject("user", request.user.username)
        action = Action(IAMMeta.FLOW_VIEW_ACTION)
        resources_list = res_factory.resources_list_for_flows([template["id"] for template in template_list], tenant_id)
        iam = get_iam_client(tenant_id)
        if not resources_list:
            return

        resources_map = {}
        for resources in resources_list:
            resources_map[resources[0].id] = resources

        request = Request(IAMMeta.SYSTEM_ID, subject, action, [], {})
        result = iam.batch_is_allowed(request, resources_list)

        if not result:
            raise MultiAuthFailedException(IAMMeta.SYSTEM_ID, subject, action, resources_list)

        not_allowed_list = []
        for tid, allow in result.items():
            if not allow:
                not_allowed_list.append(resources_map[tid])

        if not_allowed_list:
            raise MultiAuthFailedException(IAMMeta.SYSTEM_ID, subject, action, not_allowed_list)


class ExportInterceptor(ViewInterceptor):
    def process(self, request, *args, **kwargs):

        data = request.data
        template_id_list = data["template_id_list"]
        tenant_id = request.user.tenant_id
        iam = get_iam_client(tenant_id)
        subject = Subject("user", request.user.username)
        action = Action(IAMMeta.FLOW_VIEW_ACTION)
        resources_list = res_factory.resources_list_for_flows(template_id_list, tenant_id)

        if not resources_list:
            return

        resources_map = {}
        for resources in resources_list:
            resources_map[resources[0].id] = resources

        request = Request(IAMMeta.SYSTEM_ID, subject, action, [], {})
        result = iam.batch_is_allowed(request, resources_list)

        if not result:
            raise MultiAuthFailedException(IAMMeta.SYSTEM_ID, subject, action, resources_list)

        not_allowed_list = []
        for tid, allow in result.items():
            if not allow:
                not_allowed_list.append(resources_map[tid])

        if not_allowed_list:
            raise MultiAuthFailedException(IAMMeta.SYSTEM_ID, subject, action, not_allowed_list)


class ImportInterceptor(ViewInterceptor):
    def process(self, request, *args, **kwargs):
        project_id = kwargs["project_id"]
        tenant_id = request.user.tenant_id
        iam = get_iam_client(tenant_id)
        templates_data = read_template_data_file(request.FILES["data_file"])["data"]["template_data"]
        request.FILES["data_file"].seek(0)
        override = string_to_boolean(request.POST["override"])

        check_info = TaskTemplate.objects.import_operation_check(templates_data, project_id)

        subject = Subject("user", request.user.username)

        create_action = Action(IAMMeta.FLOW_CREATE_ACTION)
        project_resources = res_factory.resources_for_project(project_id, tenant_id)
        create_request = Request(IAMMeta.SYSTEM_ID, subject, create_action, project_resources, {})

        # check flow create permission
        if not override:
            allowed = iam.is_allowed(create_request)

            if not allowed:
                raise AuthFailedException(IAMMeta.SYSTEM_ID, subject, create_action, project_resources)

        else:

            # check flow create permission
            if len(check_info["new_template"]) != len(check_info["override_template"]):
                allowed = iam.is_allowed(create_request)

                if not allowed:
                    raise AuthFailedException(IAMMeta.SYSTEM_ID, subject, create_action, project_resources)

            # check flow edit permission
            if check_info["override_template"]:
                tids = [template_info["id"] for template_info in check_info["override_template"]]

                resources_list = res_factory.resources_list_for_flows(tids, tenant_id)

                if not resources_list:
                    return

                resources_map = {}
                for resources in resources_list:
                    resources_map[resources[0].id] = resources

                edit_action = Action(IAMMeta.FLOW_EDIT_ACTION)
                edit_request = Request(IAMMeta.SYSTEM_ID, subject, edit_action, [], {})
                result = iam.batch_is_allowed(edit_request, resources_list)
                if not result:
                    raise MultiAuthFailedException(IAMMeta.SYSTEM_ID, subject, edit_action, resources_list)

                not_allowed_list = []
                for tid, allow in result.items():
                    if not allow:
                        not_allowed_list.append(resources_map[tid])

                if not_allowed_list:
                    raise MultiAuthFailedException(IAMMeta.SYSTEM_ID, subject, edit_action, not_allowed_list)


class AgentGenerateProcessInterceptor(ViewInterceptor):
    def process(self, request, *args, **kwargs):
        data = json.loads(request.body)
        project_id = data.get("project_id")
        tenant_id = request.user.tenant_id
        iam = get_iam_client(tenant_id)

        subject = Subject("user", request.user.username)
        action = Action(IAMMeta.FLOW_CREATE_ACTION)
        resources = res_factory.resources_for_project(project_id, tenant_id)
        iam_request = Request(IAMMeta.SYSTEM_ID, subject, action, resources, {})

        if not iam.is_allowed(iam_request):
            raise AuthFailedException(IAMMeta.SYSTEM_ID, subject, action, resources)


class ConstantPreviewInterceptor(ViewInterceptor):
    """变量预览接口(get_constant_preview_result)的项目级 IAM 校验。

    该接口接收前端传入的任意 constants 并在 web 进程内做 Mako 渲染，历史上仅有
    @require_POST、无任何权限校验，导致任意登录用户即可触发渲染(叠加 Mako 模板注入
    时构成 RCE/越权)。这里按前端实际传参补齐鉴权:

    * 普通项目流程: 请求体 ``extra_data.project_id`` 存在 -> 校验该项目 FLOW_CREATE;
    * 公共流程: 无 project_id -> 校验系统级 COMMON_FLOW_CREATE。

    请求体非法或项目不存在时统一按鉴权失败(403)处理, 避免抛 500 形成探测面。
    """

    def process(self, request, *args, **kwargs):
        subject = Subject("user", request.user.username)
        tenant_id = request.user.tenant_id
        iam = get_iam_client(tenant_id)

        try:
            data = json.loads(request.body)
            extra_data = data.get("extra_data") or {}
            project_id = extra_data.get("project_id")
        except (ValueError, TypeError, AttributeError):
            action = Action(IAMMeta.COMMON_FLOW_CREATE_ACTION)
            raise AuthFailedException(IAMMeta.SYSTEM_ID, subject, action, [])

        if project_id:
            action = Action(IAMMeta.FLOW_CREATE_ACTION)
            try:
                resources = res_factory.resources_for_project(project_id, tenant_id)
            except Project.DoesNotExist:
                raise AuthFailedException(IAMMeta.SYSTEM_ID, subject, action, [])
            iam_request = Request(IAMMeta.SYSTEM_ID, subject, action, resources, {})
            if not iam.is_allowed(iam_request):
                raise AuthFailedException(IAMMeta.SYSTEM_ID, subject, action, resources)
            return

        # 公共流程(无 project_id): 系统级 COMMON_FLOW_CREATE
        action = Action(IAMMeta.COMMON_FLOW_CREATE_ACTION)
        iam_request = Request(IAMMeta.SYSTEM_ID, subject, action, [], {})
        if not iam.is_allowed(iam_request):
            raise AuthFailedException(IAMMeta.SYSTEM_ID, subject, action, [])


class AgentBeautifyTemplateLayoutInterceptor(ViewInterceptor):
    def process(self, request, *args, **kwargs):
        template_id = request.GET.get("template_id")
        tenant_id = request.user.tenant_id
        iam = get_iam_client(tenant_id)
        subject = Subject("user", request.user.username)
        action = Action(IAMMeta.FLOW_VIEW_ACTION)

        resources = res_factory.resources_for_flow(template_id, tenant_id)
        iam_request = Request(IAMMeta.SYSTEM_ID, subject, action, resources, {})

        if not iam.is_allowed(iam_request):
            raise AuthFailedException(IAMMeta.SYSTEM_ID, subject, action, resources)
