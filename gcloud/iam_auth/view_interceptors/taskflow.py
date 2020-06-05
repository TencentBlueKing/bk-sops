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

import abc
import ujson as json

from iam import Resource, Action, Subject, Request
from iam.exceptions import AuthFailedException

from gcloud.iam_auth import IAMMeta
from gcloud.iam_auth import get_iam_client
from gcloud.iam_auth.intercept import ViewInterceptor
from gcloud.taskflow3.models import TaskFlowInstance

iam = get_iam_client()


class TaskSingleActionInterceptor(ViewInterceptor, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get_task_id(self, request, *args, **kwargs):
        raise NotImplementedError()

    def process(self, request, *args, **kwargs):
        task_id = self.get_task_id(request, *args, **kwargs)

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


class NodesActionInpterceptor(TaskSingleActionPostInterceptor):
    action = IAMMeta.TASK_OPERATE_ACTION


class SpecNodesTimerResetInpterceptor(TaskSingleActionPostInterceptor):
    action = IAMMeta.TASK_OPERATE_ACTION


class TaskCloneInpterceptor(TaskSingleActionPostInterceptor):
    action = IAMMeta.TASK_CLONE_ACTION


class TaskModifyInputsInterceptor(TaskSingleActionPostInterceptor):
    action = IAMMeta.TASK_EDIT_ACTION


class TaskFuncClaimInterceptor(TaskSingleActionPostInterceptor):
    action = IAMMeta.TASK_CLAIM_ACTION


class GetNodeLogInterceptor(TaskSingleActionGetInterceptor):
    action = IAMMeta.TASK_VIEW_ACTION
