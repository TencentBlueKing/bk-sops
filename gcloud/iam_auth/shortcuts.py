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

from django.conf import settings

from iam import Request, MultiActionRequest, Subject, Action, Resource, IAM

from gcloud.core.models import Project

from .conf import IAMMeta


def get_iam_client():
    return IAM(settings.APP_CODE, settings.SECRET_KEY, settings.BK_IAM_INNER_HOST, settings.BK_PAAS_HOST)


def get_user_projects(username):
    subject = Subject("user", username)
    action = Action(IAMMeta.PROJECT_VIEW_ACTION)

    request = Request(IAMMeta.SYSTEM_ID, subject, action, [], {})

    key_mapping = {"project.id": "id"}

    iam = get_iam_client()
    filters = iam.make_filter(request, key_mapping=key_mapping)

    if not filters:
        return []

    return Project.objects.filter(filters)


def filter_flows_can_create_task(username, flows_id):
    iam_result = get_resources_allowed_actions_for_user(
        username,
        IAMMeta.SYSTEM_ID,
        [IAMMeta.FLOW_CREATE_TASK_ACTION],
        [[Resource(IAMMeta.SYSTEM_ID, IAMMeta.FLOW_RESOURCE, rid, {}) for rid in flows_id]],
    )

    allowed_flows_id = set()

    if not iam_result:
        return allowed_flows_id

    for rid, action_allow in iam_result.items():
        if action_allow.get(IAMMeta.FLOW_CREATE_TASK_ACTION):
            allowed_flows_id.add(rid)

    return allowed_flows_id


def get_resources_allowed_actions_for_user(username, system_id, actions, resources_list):
    subject = Subject("user", username)
    actions = [Action(act) for act in actions]
    request = MultiActionRequest(system_id, subject, actions, [], {})

    iam = get_iam_client()
    return iam.batch_resource_multi_actions_allowed(request, resources_list)
