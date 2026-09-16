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

from gcloud.iam_auth.conf import IAMMeta

# Keep the creator semantics declared by the last IAM V3
# ``upsert_resource_creator_actions`` migration. System actions are not
# resource-creator permissions. Project actions are deliberately excluded:
# projects are synchronized from CMDB and the V3 application never registered
# a Project creator-grant signal.
CREATOR_ACTIONS_BY_RESOURCE = {
    IAMMeta.FLOW_RESOURCE: {
        IAMMeta.FLOW_VIEW_ACTION,
        IAMMeta.FLOW_EDIT_ACTION,
        IAMMeta.FLOW_DELETE_ACTION,
        IAMMeta.FLOW_CREATE_TASK_ACTION,
        IAMMeta.FLOW_CREATE_MINI_APP_ACTION,
        IAMMeta.FLOW_CREATE_PERIODIC_TASK_ACTION,
        IAMMeta.FLOW_CREATE_CLOCKED_TASK_ACTION,
    },
    IAMMeta.TASK_RESOURCE: {
        IAMMeta.TASK_VIEW_ACTION,
        IAMMeta.TASK_EDIT_ACTION,
        IAMMeta.TASK_OPERATE_ACTION,
        IAMMeta.TASK_CLAIM_ACTION,
        IAMMeta.TASK_DELETE_ACTION,
        IAMMeta.TASK_CLONE_ACTION,
    },
    IAMMeta.COMMON_FLOW_RESOURCE: {
        IAMMeta.COMMON_FLOW_VIEW_ACTION,
        IAMMeta.COMMON_FLOW_EDIT_ACTION,
        IAMMeta.COMMON_FLOW_DELETE_ACTION,
    },
    IAMMeta.MINI_APP_RESOURCE: {
        IAMMeta.MINI_APP_VIEW_ACTION,
        IAMMeta.MINI_APP_EDIT_ACTION,
        IAMMeta.MINI_APP_DELETE_ACTION,
        IAMMeta.MINI_APP_CREATE_TASK_ACTION,
    },
    IAMMeta.PERIODIC_TASK_RESOURCE: {
        IAMMeta.PERIODIC_TASK_VIEW_ACTION,
        IAMMeta.PERIODIC_TASK_EDIT_ACTION,
        IAMMeta.PERIODIC_TASK_DELETE_ACTION,
    },
    IAMMeta.CLOCKED_TASK_RESOURCE: {
        IAMMeta.CLOCKED_TASK_VIEW_ACTION,
        IAMMeta.CLOCKED_TASK_EDIT_ACTION,
        IAMMeta.CLOCKED_TASK_DELETE_ACTION,
    },
}


def creator_action_allowed(username, action_id, resource):
    """Whether a locally built resource grants this action to its creator."""
    if resource is None or action_id not in CREATOR_ACTIONS_BY_RESOURCE.get(resource.type, set()):
        return False
    return (resource.attribute or {}).get("iam_resource_owner") == username


def has_creator_action(resource_type, action_id):
    return action_id in CREATOR_ACTIONS_BY_RESOURCE.get(resource_type, set())


def get_flow_creator_ids(username, tenant_id, template_ids, project_id=None):
    """Return tenant-scoped project flow IDs created by the current user."""
    from gcloud.tasktmpl3.models import TaskTemplate

    filters = {
        "id__in": template_ids,
        "project__tenant_id": tenant_id,
        "is_deleted": False,
        "pipeline_template__isnull": False,
        "pipeline_template__creator": username,
    }
    if project_id is not None:
        filters["project_id"] = project_id
    return {str(template_id) for template_id in TaskTemplate.objects.filter(**filters).values_list("id", flat=True)}


def is_flow_creator(username, tenant_id, template_id, project_id=None):
    """Return whether the tenant-scoped project flow belongs to the current user."""
    return str(template_id) in get_flow_creator_ids(username, tenant_id, [template_id], project_id=project_id)


def get_task_creator_ids(username, tenant_id, task_ids):
    """Return tenant-scoped task IDs created by the current user."""
    from gcloud.taskflow3.models import TaskFlowInstance

    return {
        str(task_id)
        for task_id in TaskFlowInstance.objects.filter(
            id__in=task_ids,
            project__tenant_id=tenant_id,
            is_deleted=False,
            pipeline_instance__isnull=False,
            pipeline_instance__creator=username,
        ).values_list("id", flat=True)
    }


def is_task_creator(username, tenant_id, task_id):
    """Return whether the tenant-scoped task belongs to the current user."""
    return str(task_id) in get_task_creator_ids(username, tenant_id, [task_id])
