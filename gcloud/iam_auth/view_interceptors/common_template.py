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

from iam import Action, Request, Subject
from iam.exceptions import AuthFailedException, MultiAuthFailedException

from gcloud.common_template.models import CommonTemplate
from gcloud.iam_auth import IAMMeta, get_iam_client, res_factory
from gcloud.iam_auth.intercept import ViewInterceptor
from gcloud.template_base.utils import read_template_data_file
from gcloud.utils.strings import string_to_boolean


class CommonTemplateViewInterceptor(ViewInterceptor):
    def process(self, request, *args, **kwargs):
        template_id = request.GET.get("template_id")
        tenant_id = request.user.tenant_id
        subject = Subject("user", request.user.username)

        iam = get_iam_client(tenant_id)
        action = Action(IAMMeta.COMMON_FLOW_VIEW_ACTION)
        resources = res_factory.resources_for_common_flow(template_id, tenant_id)
        request = Request(IAMMeta.SYSTEM_ID, subject, action, resources, {})

        allowed = iam.is_allowed(request)

        if not allowed:
            raise AuthFailedException(IAMMeta.SYSTEM_ID, subject, action, resources)


class FormInterceptor(CommonTemplateViewInterceptor):
    pass


class ParentsInterceptor(CommonTemplateViewInterceptor):
    pass


class ExportInterceptor(ViewInterceptor):
    def process(self, request, *args, **kwargs):

        data = request.data
        tenant_id = request.user.tenant_id
        iam = get_iam_client(tenant_id)
        template_id_list = data["template_id_list"]

        subject = Subject("user", request.user.username)
        action = Action(IAMMeta.COMMON_FLOW_VIEW_ACTION)
        resources_list = res_factory.resources_list_for_common_flows(template_id_list, tenant_id)

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
        templates_data = read_template_data_file(request.FILES["data_file"])["data"]["template_data"]
        tenant_id = request.user.tenant_id
        request.FILES["data_file"].seek(0)
        override = string_to_boolean(request.POST["override"])
        iam = get_iam_client(tenant_id)

        check_info = CommonTemplate.objects.import_operation_check(templates_data)

        subject = Subject("user", request.user.username)

        create_action = Action(IAMMeta.COMMON_FLOW_CREATE_ACTION)
        create_request = Request(IAMMeta.SYSTEM_ID, subject, create_action, [], {})

        # check flow create permission
        if not override:
            allowed = iam.is_allowed(create_request)

            if not allowed:
                raise AuthFailedException(IAMMeta.SYSTEM_ID, subject, create_action, [])

        else:

            # check flow create permission
            if len(check_info["new_template"]) != len(check_info["override_template"]):
                allowed = iam.is_allowed(create_request)

                if not allowed:
                    raise AuthFailedException(IAMMeta.SYSTEM_ID, subject, create_action, [])

            # check flow edit permission
            if check_info["override_template"]:
                tids = [template_info["id"] for template_info in check_info["override_template"]]

                resources_list = res_factory.resources_list_for_common_flows(tids, tenant_id)

                if not resources_list:
                    return

                resources_map = {}
                for resources in resources_list:
                    resources_map[resources[0].id] = resources

                edit_action = Action(IAMMeta.COMMON_FLOW_EDIT_ACTION)
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
