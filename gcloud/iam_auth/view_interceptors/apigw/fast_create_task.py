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

from iam import Action, Subject
from iam.contrib.tastypie.shortcuts import allow_or_raise_immediate_response_for_resources_list
from iam.shortcuts import allow_or_raise_auth_failed

from gcloud.iam_auth import IAMMeta, get_iam_client, res_factory
from gcloud.iam_auth.intercept import ViewInterceptor


class FastCreateTaskInterceptor(ViewInterceptor):
    def process(self, request, *args, **kwargs):
        if request.is_trust:
            return

        tenant_id = request.user.tenant_id
        iam = get_iam_client(tenant_id)
        project = request.project

        subject = Subject("user", request.user.username)
        action = Action(IAMMeta.PROJECT_FAST_CREATE_TASK_ACTION)
        resources = res_factory.resources_for_project_obj(project)
        allow_or_raise_auth_failed(iam, IAMMeta.SYSTEM_ID, subject, action, resources, cache=True)

        params = request.params_json
        has_common_subprocess = params.get("has_common_subprocess", False)
        templates_in_task = set()
        pipeline_tree = params["pipeline_tree"]
        for activity in pipeline_tree["activities"].values():
            if "template_id" in activity:
                templates_in_task.add(activity["template_id"])
        if not has_common_subprocess:
            action = Action(IAMMeta.FLOW_VIEW_ACTION)
            resources_list = res_factory.resources_list_for_flows(list(templates_in_task), tenant_id)
        else:
            action = Action(IAMMeta.COMMON_FLOW_VIEW_ACTION)
            resources_list = res_factory.resources_list_for_common_flows(list(templates_in_task), tenant_id)
        allow_or_raise_immediate_response_for_resources_list(
            iam=iam,
            system=IAMMeta.SYSTEM_ID,
            subject=subject,
            action=action,
            resources_list=resources_list,
        )
