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

from iam import Resource, Action, Subject
from iam.shortcuts import allow_or_raise_auth_failed

from gcloud.iam_auth import IAMMeta
from gcloud.iam_auth import get_iam_client
from gcloud.iam_auth.intercept import ViewInterceptor
from gcloud.taskflow3.models import TaskFlowInstance

iam = get_iam_client()


class TaskViewInterceptor(ViewInterceptor):
    def process(self, request, *args, **kwargs):
        if request.is_trust:
            return

        task_id = kwargs["task_id"]
        task_info = TaskFlowInstance.objects.fetch_values(
            task_id, "pipeline_instance__creator", "pipeline_instance__name", "project_id"
        )

        subject = Subject(request.user.username)
        action = Action(IAMMeta.TASK_VIEW_ACTION)
        resources = [
            Resource(
                IAMMeta.SYSTEM_ID,
                IAMMeta.TASK_RESOURCE,
                str(task_id),
                {
                    "iam_resource_owner": task_info["pipeline_instance__creator"],
                    "path": "/project,{}/".format(task_info["project_id"]),
                    "name": task_info["pipeline_instance__name"],
                },
            )
        ]
        allow_or_raise_auth_failed(iam, IAMMeta.SYSTEM_ID, subject, action, resources)
