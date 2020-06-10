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

from iam import Resource, Action, Subject
from iam.shortcuts import allow_or_raise_auth_failed

from gcloud.iam_auth import IAMMeta
from gcloud.iam_auth import get_iam_client
from gcloud.iam_auth.intercept import ViewInterceptor
from gcloud.constants import PROJECT
from gcloud.tasktmpl3.models import TaskTemplate
from gcloud.tasktmpl3.constants import NON_COMMON_TEMPLATE_TYPES
from gcloud.commons.template.models import CommonTemplate

iam = get_iam_client()


class CreateTaskInterceptor(ViewInterceptor):
    def process(self, request, *args, **kwargs):
        if request.is_trust:
            return

        params = json.loads(request.body)
        template_source = params.get("template_source", PROJECT)
        template_id = kwargs["template_id"]
        project_id = request.project.id
        subject = Subject("user", request.user.username)

        if template_source in NON_COMMON_TEMPLATE_TYPES:
            template_info = TaskTemplate.objects.fetch_values(
                template_id, "pipeline_template__creator", "pipeline_template__name", "project_id"
            )
            action = Action(IAMMeta.FLOW_CREATE_TASK_ACTION)
            resources = [
                Resource(
                    IAMMeta.SYSTEM_ID,
                    IAMMeta.FLOW_RESOURCE,
                    str(template_id),
                    {
                        "iam_resource_owner": template_info["pipeline_template__creator"],
                        "path": "/project,{}/".format(template_info["project_id"]),
                        "name": template_info["pipeline_template__name"],
                    },
                )
            ]
            allow_or_raise_auth_failed(iam, IAMMeta.SYSTEM_ID, subject, action, resources)

        else:
            template_info = CommonTemplate.objects.fetch_values(
                template_id, "pipeline_template__creator", "pipeline_template__name"
            )
            action = Action(IAMMeta.COMMON_FLOW_CREATE_TASK_ACTION)
            resources = [
                Resource(IAMMeta.SYSTEM_ID, IAMMeta.PROJECT_RESOURCE, str(project_id), {}),
                Resource(
                    IAMMeta.SYSTEM_ID,
                    IAMMeta.COMMON_FLOW_RESOURCE,
                    str(template_id),
                    {
                        "iam_resource_owner": template_info["pipeline_template__creator"],
                        "name": template_info["pipeline_template__name"],
                    },
                ),
            ]
            allow_or_raise_auth_failed(iam, IAMMeta.SYSTEM_ID, subject, action, resources)
