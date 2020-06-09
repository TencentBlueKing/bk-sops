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

from iam import Request, MultiActionRequest, Subject, Action, Resource

from gcloud.core.models import Project
from gcloud.tasktmpl3.models import TaskTemplate
from gcloud.commons.template.models import CommonTemplate
from gcloud.contrib.appmaker.models import AppMaker

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
    flows = TaskTemplate.objects.filter(id__in=flow_id_list).values("id", "pipeline_template__creator", "project_id")

    if not flows:
        return {}

    return get_resources_allowed_actions_for_user(
        username,
        IAMMeta.SYSTEM_ID,
        actions,
        [
            [
                Resource(
                    IAMMeta.SYSTEM_ID,
                    IAMMeta.FLOW_RESOURCE,
                    str(flow["id"]),
                    {
                        "iam_resource_owner": flow["pipeline_template__creator"],
                        "path": "/project,{}/".format(flow["project_id"]),
                    },
                )
            ]
            for flow in flows
        ],
    )


def get_common_flow_allowed_actions_for_user(username, actions, common_flow_id_list):
    common_flows = CommonTemplate.objects.filter(id__in=common_flow_id_list).values("id", "pipeline_template__creator")

    if not common_flows:
        return {}

    return get_resources_allowed_actions_for_user(
        username,
        IAMMeta.SYSTEM_ID,
        actions,
        [
            [
                Resource(
                    IAMMeta.SYSTEM_ID,
                    IAMMeta.COMMON_FLOW_RESOURCE,
                    str(flow["id"]),
                    {"iam_resource_owner": flow["pipeline_template__creator"]},
                )
            ]
            for flow in common_flows
        ],
    )


def get_mini_app_allowed_actions_for_user(username, actions, mini_app_id_list):
    mini_apps = AppMaker.objects.filter(id__in=mini_app_id_list).values("id", "creator", "project_id")

    if not mini_apps:
        return {}

    return get_resources_allowed_actions_for_user(
        username,
        IAMMeta.SYSTEM_ID,
        actions,
        [
            [
                Resource(
                    IAMMeta.SYSTEM_ID,
                    IAMMeta.MINI_APP_RESOURCE,
                    str(app["id"]),
                    {"iam_resource_owner": app["creator"], "path": "/project,{}/".format(app["project_id"])},
                )
            ]
            for app in mini_apps
        ],
    )


def get_resources_allowed_actions_for_user(username, system_id, actions, resources_list):
    subject = Subject("user", username)
    actions = [Action(act) for act in actions]
    request = MultiActionRequest(system_id, subject, actions, [], {})

    iam = get_iam_client()
    return iam.batch_resource_multi_actions_allowed(request, resources_list)
