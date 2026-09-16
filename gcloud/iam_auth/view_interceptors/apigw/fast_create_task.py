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

from gcloud.iam_auth import IAMMeta, PermissionCheck, PermissionService
from gcloud.iam_auth.intercept import ViewInterceptor
from gcloud.iam_auth.request_resources import load_resource_for_request


class FastCreateTaskInterceptor(ViewInterceptor):
    def process(self, request, *args, **kwargs):
        tenant_id = request.user.tenant_id
        project = request.project
        project_resource = load_resource_for_request(request, IAMMeta.PROJECT_RESOURCE, project.id)

        params = request.params_json
        has_common_subprocess = params.get("has_common_subprocess", False)
        templates_in_task = set()
        pipeline_tree = params["pipeline_tree"]
        for activity in pipeline_tree["activities"].values():
            if "template_id" in activity:
                templates_in_task.add(activity["template_id"])
        if not has_common_subprocess:
            action_id = IAMMeta.FLOW_VIEW_ACTION
            resource_type = IAMMeta.FLOW_RESOURCE
        else:
            action_id = IAMMeta.COMMON_FLOW_VIEW_ACTION
            resource_type = IAMMeta.COMMON_FLOW_RESOURCE
        template_resources = [
            load_resource_for_request(request, resource_type, template_id) for template_id in templates_in_task
        ]
        if request.is_trust:
            return
        service = PermissionService()
        service.require(
            request.user.username,
            tenant_id,
            PermissionCheck(IAMMeta.PROJECT_FAST_CREATE_TASK_ACTION, project_resource),
        )
        service.require_resources(request.user.username, tenant_id, action_id, template_resources)
