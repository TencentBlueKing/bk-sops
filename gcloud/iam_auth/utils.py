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
import logging

from gcloud.core.models import Project
from gcloud.iam_auth.constants import HTTP_AUTH_FORBIDDEN_CODE
from gcloud.iam_auth.exceptions import AuthFailedException, MultiAuthFailedException, RawAuthFailedException
from gcloud.iam_auth.models import Action, MultiActionRequest, Request, Subject
from gcloud.iam_auth.shortcuts import allow_or_raise_auth_failed

from . import res_factory
from .conf import COMMON_FLOW_PROJECT_ACTION_PAIRS, IAMMeta
from .service import PermissionService
from .shortcuts import get_iam_client

logger = logging.getLogger("root")


def get_user_projects(username, tenant_id):
    subject = Subject("user", username)
    action = Action(IAMMeta.PROJECT_VIEW_ACTION)

    request = Request(IAMMeta.SYSTEM_ID, subject, action, [], {})

    key_mapping = {"project.id": "id"}

    iam = get_iam_client(tenant_id)
    filters = iam.make_filter(request, key_mapping=key_mapping)

    if not filters:
        return Project.objects.none()
    # TODO 多租户IAM适配
    return Project.objects.filter(filters).filter(tenant_id=tenant_id)


def get_flow_allowed_actions_for_user(username, actions, flow_id_list, tenant_id):
    resources_list = res_factory.resources_list_for_flows(flow_id_list, tenant_id)

    if not resources_list:
        return {}

    return get_resources_allowed_actions_for_user(
        username,
        IAMMeta.SYSTEM_ID,
        actions,
        res_factory.resources_list_for_flows(flow_id_list, tenant_id),
        tenant_id,
    )


def get_common_flow_allowed_actions_for_user(username, actions, common_flow_id_list, tenant_id):
    resources_list = res_factory.resources_list_for_common_flows(common_flow_id_list, tenant_id)

    if not resources_list:
        return {}

    return get_resources_allowed_actions_for_user(
        username,
        IAMMeta.SYSTEM_ID,
        actions,
        resources_list,
        tenant_id,
    )


def get_mini_app_allowed_actions_for_user(username, actions, mini_app_id_list, tenant_id):
    resources_list = res_factory.resources_list_for_mini_apps(mini_app_id_list, tenant_id)

    if not resources_list:
        return {}

    return get_resources_allowed_actions_for_user(
        username,
        IAMMeta.SYSTEM_ID,
        actions,
        resources_list,
        tenant_id,
    )


def get_task_allowed_actions_for_user(username, actions, task_id_list, tenant_id):
    resources_list = res_factory.resources_list_for_tasks(task_id_list, tenant_id)

    if not resources_list:
        return {}

    return get_resources_allowed_actions_for_user(username, IAMMeta.SYSTEM_ID, actions, resources_list, tenant_id)


def get_periodic_task_allowed_actions_for_user(username, actions, periodic_task_id_list, tenant_id):
    resources_list = res_factory.resources_list_for_periodic_tasks(periodic_task_id_list, tenant_id)

    if not resources_list:
        return {}

    return get_resources_allowed_actions_for_user(username, IAMMeta.SYSTEM_ID, actions, resources_list, tenant_id)


def get_resources_allowed_actions_for_user(username, system_id, actions, resources_list, tenant_id):
    subject = Subject("user", username)
    actions = [Action(act) for act in actions]
    request = MultiActionRequest(system_id, subject, actions, [], {})

    iam = get_iam_client(tenant_id)
    return iam.batch_resource_multi_actions_allowed(request, resources_list)


def iam_multi_resource_auth_or_raise(username, action, resource_ids, get_resource_func, tenant_id):
    iam = get_iam_client(tenant_id)
    action = Action(action)
    subject = Subject("user", username)
    resource_list = getattr(res_factory, get_resource_func)(resource_ids, tenant_id)
    if not resource_list:
        return
    resource_map = {resource[0].id: resource for resource in resource_list}
    request = Request(IAMMeta.SYSTEM_ID, subject, action, [], {})
    result = iam.batch_is_allowed(request, resource_list)
    if not result:
        raise MultiAuthFailedException(IAMMeta.SYSTEM_ID, subject, action, resource_list)
    not_allowed_list = []
    for tid, allow in result.items():
        if not allow:
            not_allowed_list.append(resource_map[tid])

    if not_allowed_list:
        raise MultiAuthFailedException(IAMMeta.SYSTEM_ID, subject, action, not_allowed_list)


def iam_resource_auth_or_raise(username, action, tenant_id, resource_id=None, get_resource_func=None):
    iam = get_iam_client(tenant_id)
    action = Action(action)
    subject = Subject("user", username)
    resources = None
    if get_resource_func:
        resources = getattr(res_factory, get_resource_func)(resource_id, tenant_id)
    request = Request(IAMMeta.SYSTEM_ID, subject, action, resources or [], {})
    if not iam.is_allowed(request):
        raise AuthFailedException(IAMMeta.SYSTEM_ID, subject, action, resources or [])


def check_project_or_admin_view_action_for_user(project_id, username, tenant_id):
    iam = get_iam_client(tenant_id)
    action = Action(IAMMeta.PROJECT_VIEW_ACTION) if project_id else Action(IAMMeta.ADMIN_VIEW_ACTION)
    resources = res_factory.resources_for_project(project_id, tenant_id) if project_id else []
    allow_or_raise_auth_failed(
        iam=iam,
        system=IAMMeta.SYSTEM_ID,
        subject=Subject("user", username),
        action=action,
        resources=resources,
    )


def check_and_raise_raw_auth_fail_exception(result: dict, message=None):
    if result.get("code", 0) == HTTP_AUTH_FORBIDDEN_CODE:
        logger.warning(message or result.get("message", "[check_and_raise_raw_auth_fail_exception]"))
        raise RawAuthFailedException(permissions=result.get("permission", {}))


def get_common_flow_allowed_actions_for_user_and_project(username, actions, common_flow_id_list, project_id, tenant_id):
    resources_list = res_factory.resources_list_for_common_flows(common_flow_id_list, tenant_id)
    if not resources_list or not project_id:
        return {}
    project_resources = res_factory.resources_for_project(project_id, tenant_id)
    if not project_resources:
        return {}
    result = get_resources_allowed_actions_for_user(
        username,
        IAMMeta.SYSTEM_ID,
        actions,
        resources_list,
        tenant_id,
    )
    service = PermissionService()
    for common_action, project_action in COMMON_FLOW_PROJECT_ACTION_PAIRS.items():
        if common_action not in actions:
            continue
        project_decisions = service.allowed_actions(
            username,
            tenant_id,
            [project_action, IAMMeta.PROJECT_VIEW_ACTION],
            project_resources[0],
        )
        project_allowed = all(project_decisions.values())
        for decisions in result.values():
            decisions[common_action] = decisions.get(common_action, False) and project_allowed
            decisions[project_action] = project_decisions[project_action]
            decisions[IAMMeta.PROJECT_VIEW_ACTION] = project_decisions[IAMMeta.PROJECT_VIEW_ACTION]
    return result
