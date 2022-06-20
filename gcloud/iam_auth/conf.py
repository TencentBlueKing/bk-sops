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

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from iam import meta

SYSTEM_ID = settings.BK_IAM_SYSTEM_ID

SYSTEM_INFO = [
    {"id": SYSTEM_ID, "name": settings.APP_NAME},
]

SEARCH_INSTANCE_CACHE_TIME = 60 * 10

RESOURCES = [
    {"id": "project", "name": _("项目"), "parent_id": None},
    {"id": "flow", "name": _("流程模板"), "parent_id": "project"},
    {"id": "task", "name": _("任务实例"), "parent_id": "project"},
    {"id": "common_flow", "name": _("公共流程"), "parent_id": None},
    {"id": "mini_app", "name": _("轻应用"), "parent_id": "project"},
    {"id": "periodic_task", "name": _("周期任务"), "parent_id": "project"},
    {"id": "clocked_task", "name": _("计划任务"), "parent_id": "project"},
]

ACTIONS = [
    {
        "id": "project_create",
        "name": _("创建项目"),
        "relate_resources": ["project"],
        "relate_actions": [],
        "resource_topo": ["project"],
    },
    {
        "id": "project_view",
        "name": _("查看项目"),
        "relate_resources": ["project"],
        "relate_actions": [],
        "resource_topo": ["project"],
    },
    {
        "id": "project_edit",
        "name": _("编辑项目"),
        "relate_resources": ["project"],
        "relate_actions": ["project_view"],
        "resource_topo": ["project"],
    },
    {
        "id": "flow_create",
        "name": _("创建流程"),
        "relate_resources": ["project"],
        "relate_actions": ["project_view"],
        "resource_topo": ["project", "flow"],
    },
    {
        "id": "project_fast_create_task",
        "name": _("快速新建一次性任务"),
        "relate_resources": ["project"],
        "relate_actions": ["project_view"],
        "resource_topo": ["project", "flow"],
    },
    {
        "id": "flow_view",
        "name": _("查看流程"),
        "relate_resources": ["flow"],
        "relate_actions": [],
        "resource_topo": ["project", "flow"],
    },
    {
        "id": "flow_edit",
        "name": _("编辑流程"),
        "relate_resources": ["flow"],
        "relate_actions": ["flow_view"],
        "resource_topo": ["project", "flow"],
    },
    {
        "id": "flow_delete",
        "name": _("删除流程"),
        "relate_resources": ["flow"],
        "relate_actions": ["flow_view"],
        "resource_topo": ["project", "flow"],
    },
    {
        "id": "flow_create_task",
        "name": _("使用流程新建任务"),
        "relate_resources": ["flow"],
        "relate_actions": ["flow_view"],
        "resource_topo": ["project", "flow"],
    },
    {
        "id": "flow_create_mini_app",
        "name": _("新建轻应用"),
        "relate_resources": ["flow"],
        "relate_actions": ["flow_view"],
        "resource_topo": ["project", "flow"],
    },
    {
        "id": "flow_create_periodic_task",
        "name": _("新建周期任务"),
        "relate_resources": ["flow"],
        "relate_actions": ["flow_view"],
        "resource_topo": ["project", "flow"],
    },
    {
        "id": "flow_create_clocked_task",
        "name": _("新建计划任务"),
        "relate_resources": ["flow"],
        "relate_actions": ["flow_view"],
        "resource_topo": ["project", "flow"],
    },
    {
        "id": "task_view",
        "name": _("查看任务"),
        "relate_resources": ["task"],
        "relate_actions": [],
        "resource_topo": ["project", "task"],
    },
    {
        "id": "task_edit",
        "name": _("编辑任务"),
        "relate_resources": ["task"],
        "relate_actions": ["task_view"],
        "resource_topo": ["project", "task"],
    },
    {
        "id": "task_operate",
        "name": _("操作任务"),
        "relate_resources": ["task"],
        "relate_actions": ["task_view"],
        "resource_topo": ["project", "task"],
    },
    {
        "id": "task_claim",
        "name": _("认领任务"),
        "relate_resources": ["task"],
        "relate_actions": ["task_view"],
        "resource_topo": ["project", "task"],
    },
    {
        "id": "task_delete",
        "name": _("删除任务"),
        "relate_resources": ["task"],
        "relate_actions": ["task_view"],
        "resource_topo": ["project", "task"],
    },
    {
        "id": "task_clone",
        "name": _("克隆任务"),
        "relate_resources": ["task"],
        "relate_actions": ["task_view"],
        "resource_topo": ["project", "task"],
    },
    {
        "id": "common_flow_create",
        "name": _("新建公共流程"),
        "relate_resources": [],
        "relate_actions": [],
        "resource_topo": [],
    },
    {
        "id": "common_flow_view",
        "name": _("查看公共流程"),
        "relate_resources": ["common_flow"],
        "relate_actions": [],
        "resource_topo": ["common_flow"],
    },
    {
        "id": "common_flow_edit",
        "name": _("编辑公共流程"),
        "relate_resources": ["common_flow"],
        "relate_actions": ["common_flow_view"],
        "resource_topo": ["common_flow"],
    },
    {
        "id": "common_flow_delete",
        "name": _("删除公共流程"),
        "relate_resources": ["common_flow"],
        "relate_actions": ["common_flow_view"],
        "resource_topo": ["common_flow"],
    },
    {
        "id": "common_flow_create_task",
        "name": _("使用公共流程新建任务"),
        "relate_resources": ["common_flow", "project"],
        "relate_actions": ["common_flow_view", "project_view"],
        "resource_topo": ["common_flow"],
    },
    {
        "id": "common_flow_create_periodic_task",
        "name": _("使用公共流程新建周期任务"),
        "relate_resources": ["common_flow", "project"],
        "relate_actions": ["common_flow_view", "project_view"],
        "resource_topo": ["common_flow"],
    },
    {
        "id": "mini_app_view",
        "name": _("查看轻应用"),
        "relate_resources": ["mini_app"],
        "relate_actions": [],
        "resource_topo": ["project", "mini_app"],
    },
    {
        "id": "mini_app_edit",
        "name": _("编辑轻应用"),
        "relate_resources": ["mini_app"],
        "relate_actions": ["mini_app_view"],
        "resource_topo": ["project", "mini_app"],
    },
    {
        "id": "mini_app_delete",
        "name": _("删除轻应用"),
        "relate_resources": ["mini_app"],
        "relate_actions": ["mini_app_view"],
        "resource_topo": ["project", "mini_app"],
    },
    {
        "id": "mini_app_create_task",
        "name": _("使用轻应用创建任务"),
        "relate_resources": ["mini_app"],
        "relate_actions": ["mini_app_view"],
        "resource_topo": ["project", "mini_app"],
    },
    {
        "id": "periodic_task_view",
        "name": _("查看周期任务"),
        "relate_resources": ["periodic_task"],
        "relate_actions": [],
        "resource_topo": ["project", "periodic_task"],
    },
    {
        "id": "periodic_task_edit",
        "name": _("编辑周期任务"),
        "relate_resources": ["periodic_task"],
        "relate_actions": ["periodic_task_view"],
        "resource_topo": ["project", "periodic_task"],
    },
    {
        "id": "periodic_task_delete",
        "name": _("删除周期任务"),
        "relate_resources": ["periodic_task"],
        "relate_actions": ["periodic_task_view"],
        "resource_topo": ["project", "periodic_task"],
    },
    {
        "id": "clocked_task_view",
        "name": _("查看计划任务"),
        "relate_resources": ["clocked_task"],
        "relate_actions": [],
        "resource_topo": ["project", "clocked_task"],
    },
    {
        "id": "clocked_task_edit",
        "name": _("编辑计划任务"),
        "relate_resources": ["clocked_task"],
        "relate_actions": ["clocked_task_view"],
        "resource_topo": ["project", "clocked_task"],
    },
    {
        "id": "clocked_task_delete",
        "name": _("删除计划任务"),
        "relate_resources": ["clocked_task"],
        "relate_actions": ["clocked_task_view"],
        "resource_topo": ["project", "clocked_task"],
    },
    {"id": "admin_view", "name": _("后台管理查看"), "relate_resources": [], "relate_actions": []},
    {"id": "admin_edit", "name": _("后台管理编辑"), "relate_resources": [], "relate_actions": []},
    {"id": "audit_view", "name": _("查看审计中心"), "relate_resources": [], "relate_actions": []},
    {"id": "function_view", "name": _("查看职能化中心"), "relate_resources": [], "relate_actions": []},
    {"id": "statistics_view", "name": _("查看数据统计"), "relate_resources": [], "relate_actions": []},
]


class IAMMeta(object):

    SYSTEM_ID = SYSTEM_ID

    PROJECT_RESOURCE = "project"
    FLOW_RESOURCE = "flow"
    TASK_RESOURCE = "task"
    COMMON_FLOW_RESOURCE = "common_flow"
    MINI_APP_RESOURCE = "mini_app"
    PERIODIC_TASK_RESOURCE = "periodic_task"
    CLOCKED_TASK_RESOURCE = "clocked_task"

    PROJECT_VIEW_ACTION = "project_view"
    PROJECT_EDIT_ACTION = "project_edit"
    PROJECT_FAST_CREATE_TASK_ACTION = "project_fast_create_task"

    FLOW_CREATE_ACTION = "flow_create"
    FLOW_VIEW_ACTION = "flow_view"
    FLOW_EDIT_ACTION = "flow_edit"
    FLOW_DELETE_ACTION = "flow_delete"
    FLOW_CREATE_TASK_ACTION = "flow_create_task"
    FLOW_CREATE_MINI_APP_ACTION = "flow_create_mini_app"
    FLOW_CREATE_PERIODIC_TASK_ACTION = "flow_create_periodic_task"
    FLOW_CREATE_CLOCKED_TASK_ACTION = "flow_create_clocked_task"

    TASK_VIEW_ACTION = "task_view"
    TASK_EDIT_ACTION = "task_edit"
    TASK_OPERATE_ACTION = "task_operate"
    TASK_CLAIM_ACTION = "task_claim"
    TASK_DELETE_ACTION = "task_delete"
    TASK_CLONE_ACTION = "task_clone"

    COMMON_FLOW_CREATE_TASK_ACTION = "common_flow_create_task"
    COMMON_FLOW_CREATE_ACTION = "common_flow_create"
    COMMON_FLOW_VIEW_ACTION = "common_flow_view"
    COMMON_FLOW_EDIT_ACTION = "common_flow_edit"
    COMMON_FLOW_DELETE_ACTION = "common_flow_delete"
    COMMON_FLOW_CREATE_PERIODIC_TASK_ACTION = "common_flow_create_periodic_task"

    MINI_APP_VIEW_ACTION = "mini_app_view"
    MINI_APP_EDIT_ACTION = "mini_app_edit"
    MINI_APP_DELETE_ACTION = "mini_app_delete"
    MINI_APP_CREATE_TASK_ACTION = "mini_app_create_task"

    PERIODIC_TASK_VIEW_ACTION = "periodic_task_view"
    PERIODIC_TASK_EDIT_ACTION = "periodic_task_edit"
    PERIODIC_TASK_DELETE_ACTION = "periodic_task_delete"

    CLOCKED_TASK_VIEW_ACTION = "clocked_task_view"
    CLOCKED_TASK_EDIT_ACTION = "clocked_task_edit"
    CLOCKED_TASK_DELETE_ACTION = "clocked_task_delete"

    ADMIN_VIEW_ACTION = "admin_view"
    ADMIN_EDIT_ACTION = "admin_edit"
    AUDIT_VIEW_ACTION = "audit_view"
    FUNCTION_VIEW_ACTION = "function_view"
    STATISTICS_VIEW_ACTION = "statistics_view"


for system in SYSTEM_INFO:
    meta.setup_system(system["id"], system["name"])

for resource in RESOURCES:
    meta.setup_resource(SYSTEM_ID, resource["id"], resource["name"])

for action in ACTIONS:
    meta.setup_action(SYSTEM_ID, action["id"], action["name"])


COMMON_FLOW_ACTIONS = [
    IAMMeta.COMMON_FLOW_CREATE_TASK_ACTION,
    IAMMeta.COMMON_FLOW_EDIT_ACTION,
    IAMMeta.COMMON_FLOW_DELETE_ACTION,
    IAMMeta.COMMON_FLOW_VIEW_ACTION,
    IAMMeta.COMMON_FLOW_CREATE_ACTION,
    IAMMeta.COMMON_FLOW_CREATE_PERIODIC_TASK_ACTION,
]

PERIODIC_TASK_ACTIONS = [
    IAMMeta.PERIODIC_TASK_VIEW_ACTION,
    IAMMeta.PERIODIC_TASK_DELETE_ACTION,
    IAMMeta.PERIODIC_TASK_EDIT_ACTION,
]

TASK_ACTIONS = [
    IAMMeta.TASK_VIEW_ACTION,
    IAMMeta.TASK_EDIT_ACTION,
    IAMMeta.TASK_OPERATE_ACTION,
    IAMMeta.TASK_CLAIM_ACTION,
    IAMMeta.TASK_DELETE_ACTION,
    IAMMeta.TASK_CLONE_ACTION,
]

FLOW_ACTIONS = [
    IAMMeta.FLOW_CREATE_ACTION,
    IAMMeta.FLOW_VIEW_ACTION,
    IAMMeta.FLOW_EDIT_ACTION,
    IAMMeta.FLOW_DELETE_ACTION,
    IAMMeta.FLOW_CREATE_TASK_ACTION,
    IAMMeta.FLOW_CREATE_MINI_APP_ACTION,
    IAMMeta.FLOW_CREATE_PERIODIC_TASK_ACTION,
    IAMMeta.FLOW_CREATE_CLOCKED_TASK_ACTION,
]

MINI_APP_ACTIONS = [
    IAMMeta.MINI_APP_VIEW_ACTION,
    IAMMeta.MINI_APP_EDIT_ACTION,
    IAMMeta.MINI_APP_DELETE_ACTION,
    IAMMeta.MINI_APP_CREATE_TASK_ACTION,
]

PROJECT_ACTIONS = [
    IAMMeta.PROJECT_VIEW_ACTION,
    IAMMeta.PROJECT_EDIT_ACTION,
    IAMMeta.PROJECT_FAST_CREATE_TASK_ACTION,
]
