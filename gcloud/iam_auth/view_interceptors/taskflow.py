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

from iam import Resource, Action, Subject, Request
from iam.exceptions import AuthFailedException

from gcloud.iam_auth import IAMMeta
from gcloud.iam_auth import get_iam_client
from gcloud.iam_auth.intercept import ViewInterceptor
from gcloud.taskflow3.models import TaskFlowInstance

iam = get_iam_client()


class TaskSingleActionInterceptor(ViewInterceptor):
    def process(self, request, *args, **kwargs):
        task_id = json.loads(request.body)["instance_id"]

        subject = Subject("user", request.user.username)
        action = Action(self.action)
        resources = [
            Resource(
                IAMMeta.SYSTEM_ID,
                IAMMeta.TASK_RESOURCE,
                str(task_id),
                {"iam_resource_owner": TaskFlowInstance.objects.creator_for(task_id)},
            )
        ]

        request = Request(IAMMeta.SYSTEM_ID, subject, action, resources, {})
        allowed = iam.is_allowed(request)

        if not allowed:
            raise AuthFailedException(IAMMeta.SYSTEM_ID, subject, action, resources)


class DataViewInterceptor(TaskSingleActionInterceptor):
    action = IAMMeta.TASK_VIEW_ACTION


class DetailViewInterceptor(TaskSingleActionInterceptor):
    action = IAMMeta.TASK_VIEW_ACTION


class TaskActionInterceptor(TaskSingleActionInterceptor):
    action = IAMMeta.TASK_OPERATE_ACTION


class NodesActionInpterceptor(TaskSingleActionInterceptor):
    action = IAMMeta.TASK_OPERATE_ACTION


class SpecNodesTimerResetInpterceptor(TaskSingleActionInterceptor):
    action = IAMMeta.TASK_OPERATE_ACTION


class TaskCloneInpterceptor(TaskSingleActionInterceptor):
    action = IAMMeta.TASK_CLONE_ACTION


class TaskModifyInputsInterceptor(TaskSingleActionInterceptor):
    action = IAMMeta.TASK_EDIT_ACTION


class TaskFuncClaimInterceptor(TaskSingleActionInterceptor):
    action = IAMMeta.TASK_CLAIM_ACTION


class GetNodeLogInterceptor(TaskSingleActionInterceptor):
    action = IAMMeta.TASK_VIEW_ACTION
