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

import ujson as json

from iam import Action, Subject, Request
from iam.exceptions import AuthFailedException, MultiAuthFailedException

from gcloud.utils.strings import string_to_boolean
from gcloud.tasktmpl3.models import TaskTemplate
from gcloud.commons.template.utils import read_template_data_file

from gcloud.iam_auth import IAMMeta
from gcloud.iam_auth import get_iam_client
from gcloud.iam_auth.intercept import ViewInterceptor
from gcloud.iam_auth import res_factory

iam = get_iam_client()


class FormInterceptor(ViewInterceptor):
    def process(self, request, *args, **kwargs):
        template_id = request.GET.get("template_id")

        subject = Subject("user", request.user.username)
        action = Action(IAMMeta.FLOW_VIEW_ACTION)
        resources = res_factory.resources_for_flow(template_id)
        request = Request(IAMMeta.SYSTEM_ID, subject, action, resources, {})

        allowed = iam.is_allowed(request)

        if not allowed:
            raise AuthFailedException(IAMMeta.SYSTEM_ID, subject, action, resources)


class ExportInterceptor(ViewInterceptor):
    def process(self, request, *args, **kwargs):

        data = json.loads(request.body)
        template_id_list = data["template_id_list"]

        subject = Subject("user", request.user.username)
        action = Action(IAMMeta.FLOW_VIEW_ACTION)
        resources_list = res_factory.resources_list_for_flows(template_id_list)

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
        templates_data = read_template_data_file(request.FILES["data_file"])["data"]["template_data"]
        request.FILES["data_file"].seek(0)
        override = string_to_boolean(request.POST["override"])

        check_info = TaskTemplate.objects.import_operation_check(templates_data, project_id)

        subject = Subject("user", request.user.username)

        create_action = Action(IAMMeta.FLOW_CREATE_ACTION)
        project_resources = res_factory.resources_for_project(project_id)
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

                resources_list = res_factory.resources_list_for_flows(tids)

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
