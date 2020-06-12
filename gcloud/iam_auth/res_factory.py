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

from iam import Resource

from gcloud.core.models import Project
from gcloud.commons.template.models import CommonTemplate
from gcloud.tasktmpl3.models import TaskTemplate
from gcloud.taskflow3.models import TaskFlowInstance
from gcloud.periodictask.models import PeriodicTask
from gcloud.contrib.appmaker.models import AppMaker
from gcloud.iam_auth import IAMMeta

# flow


def resources_for_flow(flow_id):
    template_info = TaskTemplate.objects.fetch_values(
        flow_id, "pipeline_template__creator", "pipeline_template__name", "project_id"
    )

    return [
        Resource(
            IAMMeta.SYSTEM_ID,
            IAMMeta.FLOW_RESOURCE,
            str(flow_id),
            {
                "iam_resource_owner": template_info["pipeline_template__creator"],
                "path": "/project,{}/".format(template_info["project_id"]),
                "name": template_info["pipeline_template__name"],
            },
        )
    ]


def resources_for_flow_obj(flow_obj):
    return [
        Resource(
            IAMMeta.SYSTEM_ID,
            IAMMeta.FLOW_RESOURCE,
            str(flow_obj.id),
            {
                "iam_resource_owner": flow_obj.creator,
                "path": "/project,{}/".format(flow_obj.project_id),
                "name": flow_obj.name,
            },
        )
    ]


def resources_list_for_flows(flow_id_list):
    qs = TaskTemplate.objects.filter(id__in=flow_id_list, is_deleted=False).values(
        "id", "pipeline_template__creator", "pipeline_template__name", "project_id"
    )

    return [
        [
            Resource(
                IAMMeta.SYSTEM_ID,
                IAMMeta.FLOW_RESOURCE,
                str(value["id"]),
                {
                    "iam_resource_owner": value["pipeline_template__creator"],
                    "path": "/project,{}/".format(value["project_id"]),
                    "name": value["pipeline_template__name"],
                },
            )
        ]
        for value in qs
    ]


# project


def resources_for_project(project_id):
    project = Project.objects.get(id=project_id)

    return [Resource(IAMMeta.SYSTEM_ID, IAMMeta.PROJECT_RESOURCE, str(project_id), {"name": project.name})]


def resources_for_project_obj(project_obj):
    return [Resource(IAMMeta.SYSTEM_ID, IAMMeta.PROJECT_RESOURCE, str(project_obj.id), {"name": project_obj.name})]


# task


def resources_for_task(task_id):
    task_info = TaskFlowInstance.objects.fetch_values(
        task_id, "pipeline_instance__creator", "pipeline_instance__name", "project_id", "flow_type"
    )

    return [
        Resource(
            IAMMeta.SYSTEM_ID,
            IAMMeta.TASK_RESOURCE,
            str(task_id),
            {
                "iam_resource_owner": task_info["pipeline_instance__creator"],
                "path": "/project,{}/".format(task_info["project_id"]),
                "name": task_info["pipeline_instance__name"],
                "type": task_info["flow_type"],
            },
        )
    ]


def resources_for_task_obj(task_obj):
    return [
        Resource(
            IAMMeta.SYSTEM_ID,
            IAMMeta.TASK_RESOURCE,
            str(task_obj.id),
            {
                "iam_resource_owner": task_obj.creator,
                "path": "/project,{}/".format(task_obj.project_id),
                "name": task_obj.name,
                "type": task_obj.flow_type,
            },
        )
    ]


# periodic_task


def resources_for_periodic_task(task_id):
    task_info = PeriodicTask.objects.fetch_values(task_id, "task__creator", "task__name", "project_id")
    return [
        Resource(
            IAMMeta.SYSTEM_ID,
            IAMMeta.PERIODIC_TASK_RESOURCE,
            str(task_id),
            {
                "iam_resource_owner": task_info["task__creator"],
                "path": "/project,{}/".format(task_info["project_id"]),
                "name": task_info["task__name"],
            },
        )
    ]


def resources_for_periodic_task_obj(task_obj):
    return [
        Resource(
            IAMMeta.SYSTEM_ID,
            IAMMeta.PERIODIC_TASK_RESOURCE,
            str(task_obj.id),
            {
                "iam_resource_owner": task_obj.creator,
                "path": "/project,{}/".format(task_obj.project_id),
                "name": task_obj.name,
            },
        )
    ]


# common flow


def resources_for_common_flow(common_flow_id):
    template_info = CommonTemplate.objects.fetch_values(
        common_flow_id, "pipeline_template__creator", "pipeline_template__name"
    )

    return [
        Resource(
            IAMMeta.SYSTEM_ID,
            IAMMeta.COMMON_FLOW_RESOURCE,
            str(common_flow_id),
            {
                "iam_resource_owner": template_info["pipeline_template__creator"],
                "name": template_info["pipeline_template__name"],
            },
        )
    ]


def resources_for_common_flow_obj(common_flow_obj):
    return [
        Resource(
            IAMMeta.SYSTEM_ID,
            IAMMeta.COMMON_FLOW_RESOURCE,
            str(common_flow_obj.id),
            {"iam_resource_owner": common_flow_obj.creator, "name": common_flow_obj.name},
        )
    ]


def resources_list_for_common_flows(common_flow_id_list):
    qs = CommonTemplate.objects.filter(id__in=common_flow_id_list, is_deleted=False).values(
        "id", "pipeline_template__creator", "pipeline_template__name"
    )

    return [
        [
            Resource(
                IAMMeta.SYSTEM_ID,
                IAMMeta.COMMON_FLOW_RESOURCE,
                str(value["id"]),
                {"iam_resource_owner": value["pipeline_template__creator"], "name": value["pipeline_template__name"]},
            )
        ]
        for value in qs
    ]


# mini app


def resources_for_mini_app_obj(mini_app_obj):
    return [
        Resource(
            IAMMeta.SYSTEM_ID,
            IAMMeta.MINI_APP_RESOURCE,
            str(mini_app_obj.id),
            {
                "iam_resource_owner": mini_app_obj.creator,
                "path": "/project,{}/".format(mini_app_obj.project_id),
                "name": mini_app_obj.name,
            },
        )
    ]


def resources_list_for_mini_apps(mini_app_id_list):
    qs = AppMaker.objects.filter(id__in=mini_app_id_list).values("id", "creator", "project_id")

    return [
        [
            Resource(
                IAMMeta.SYSTEM_ID,
                IAMMeta.MINI_APP_RESOURCE,
                str(value["id"]),
                {"iam_resource_owner": value["creator"], "path": "/project,{}/".format(value["project_id"])},
            )
        ]
        for value in qs
    ]


# function task


def resources_for_function_task_obj(task_obj):
    return [
        Resource(
            IAMMeta.SYSTEM_ID,
            IAMMeta.TASK_RESOURCE,
            str(task_obj.task_id),
            {
                "iam_resource_owner": task_obj.task.creator,
                "path": "/project,{}/".format(task_obj.task.project_id),
                "name": task_obj.task.name,
                "type": task_obj.task.flow_type,
            },
        )
    ]
