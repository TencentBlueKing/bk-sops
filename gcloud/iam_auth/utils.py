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

from iam import Request, MultiActionRequest, Subject, Action

from gcloud.core.models import Project

from . import res_factory
from .conf import IAMMeta
from .shortcuts import get_iam_client


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


def get_flow_allowed_actions_for_user(username, actions, flow_id_list):
    resources_list = res_factory.resources_list_for_flows(flow_id_list)

    if not resources_list:
        return {}

    return get_resources_allowed_actions_for_user(
        username, IAMMeta.SYSTEM_ID, actions, res_factory.resources_list_for_flows(flow_id_list),
    )


def get_common_flow_allowed_actions_for_user(username, actions, common_flow_id_list):
    resources_list = res_factory.resources_list_for_common_flows(common_flow_id_list)

    if not resources_list:
        return {}

    return get_resources_allowed_actions_for_user(username, IAMMeta.SYSTEM_ID, actions, resources_list,)


def get_mini_app_allowed_actions_for_user(username, actions, mini_app_id_list):
    resources_list = res_factory.resources_list_for_mini_apps(mini_app_id_list)

    if not resources_list:
        return {}

    return get_resources_allowed_actions_for_user(username, IAMMeta.SYSTEM_ID, actions, resources_list,)


def get_resources_allowed_actions_for_user(username, system_id, actions, resources_list):
    subject = Subject("user", username)
    actions = [Action(act) for act in actions]
    request = MultiActionRequest(system_id, subject, actions, [], {})

    iam = get_iam_client()
    return iam.batch_resource_multi_actions_allowed(request, resources_list)
