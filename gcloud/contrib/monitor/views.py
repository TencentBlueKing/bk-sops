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

from django.db.models import Q
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_GET
from pipeline.eri.models import Schedule, State

from gcloud.iam_auth.intercept import iam_intercept
from gcloud.iam_auth.view_interceptors.statistics import StatisticsViewInpterceptor
from gcloud.taskflow3.models import TaskFlowInstance
import pyrabbit2

@require_GET
@iam_intercept(StatisticsViewInpterceptor())
def get_failed_task(request):
    """
    获取失败任务
    """
    limit = int(request.GET.get("limit", 100))
    offset = int(request.GET.get("offset", 0))
    st = timezone.now() - timezone.timedelta(days=30)
    start_time = request.GET.get("start_time", st)
    states = State.objects.filter(name="FAILED", started_time__gte=start_time).values("root_id")
    root_ids = [state["root_id"] for state in states]
    tasks = (
        TaskFlowInstance.objects.select_related("project", "pipeline_instance")
        .filter(
            pipeline_instance__is_deleted=False,
            pipeline_instance__is_expired=False,
            pipeline_instance__is_finished=False,
            pipeline_instance__is_revoked=False,
            pipeline_instance__is_started=True,
            pipeline_instance__instance_id__in=root_ids,
        )
        .values("id", "project__name", "pipeline_instance__name")[offset : limit + offset]
    )
    failed_tasks = [
        {
            "task_id": task["id"],
            "project_name": task["project__name"],
            "task_name": task["pipeline_instance__name"],
        }
        for task in tasks
    ]
    return JsonResponse({"result": True, "data": failed_tasks})


@require_GET
@iam_intercept(StatisticsViewInpterceptor())
def get_executing_task(request):
    """
    获取执行中任务
    """
    limit = int(request.GET.get("limit", 100))
    offset = int(request.GET.get("offset", 0))
    st = timezone.now() - timezone.timedelta(days=30)
    start_time = request.GET.get("start_time", st)
    failed_states = State.objects.filter(name="FAILED", started_time__gte=start_time).values("root_id")
    failed_root_ids = [state["root_id"] for state in failed_states]
    # 失败的任务
    failed_tasks = (
        TaskFlowInstance.objects.select_related("project", "pipeline_instance")
        .filter(
            pipeline_instance__is_deleted=False,
            pipeline_instance__is_expired=False,
            pipeline_instance__is_finished=False,
            pipeline_instance__is_revoked=False,
            pipeline_instance__is_started=True,
            pipeline_instance__instance_id__in=failed_root_ids,
        )
        .values(
            "pipeline_instance__id",
        )[offset : limit + offset]
    )
    failed_task_ids = [task["pipeline_instance__id"] for task in failed_tasks]

    states = State.objects.filter(~Q(name="FAILED")).filter(started_time__gte=start_time).values("root_id")
    root_ids = [state["root_id"] for state in states]
    # 非失败的任务
    tasks = (
        TaskFlowInstance.objects.select_related("project", "pipeline_instance")
        .filter(
            pipeline_instance__is_deleted=False,
            pipeline_instance__is_expired=False,
            pipeline_instance__is_finished=False,
            pipeline_instance__is_revoked=False,
            pipeline_instance__is_started=True,
            pipeline_instance__instance_id__in=root_ids,
        )
        .values("id", "project__name", "pipeline_instance__name", "pipeline_instance__id")[offset : limit + offset]
    )
    # 求差获得执行中的任务
    executing_tasks = [
        {
            "task_id": task["id"],
            "project_name": task["project__name"],
            "task_name": task["pipeline_instance__name"],
        }
        for task in tasks
        if task["pipeline_instance__id"] not in failed_task_ids
    ]
    return JsonResponse({"result": True, "data": executing_tasks})


@require_GET
@iam_intercept(StatisticsViewInpterceptor())
def get_schedule_times(request):
    """
    获取调度次数
    """
    limit = int(request.GET.get("limit", 100))
    offset = int(request.GET.get("offset", 0))
    st = timezone.now() - timezone.timedelta(days=30)
    start_time = request.GET.get("start_time", st)
    schedules = Schedule.objects.filter(scheduling=False).values("node_id", "schedule_times")
    schedules = {schedule["node_id"]: schedule["schedule_times"] for schedule in schedules}
    states = State.objects.filter(started_time__gte=start_time, node_id__in=list(schedules.keys())).values(
        "node_id", "root_id"
    )
    root_ids = {state["root_id"]: schedules[state["node_id"]] for state in states}
    tasks = (
        TaskFlowInstance.objects.select_related("project", "pipeline_instance")
        .filter(pipeline_instance__instance_id__in=list(root_ids.keys()))
        .values(
            "id",
            "project__name",
            "pipeline_instance__name",
            "pipeline_instance__creator",
            "pipeline_instance__instance_id",
        )[offset : offset + limit]
    )
    schedule_times = [
        {
            "id": task["id"],
            "project_name": task["project__name"],
            "creator": task["pipeline_instance__name"],
            "schedule_times": root_ids[task["pipeline_instance__instance_id"]],
        }
        for task in tasks
    ]
    return JsonResponse({"result": True, "data": schedule_times})

@require_GET
@iam_intercept(StatisticsViewInpterceptor())
def get_mq_overview(request):
    """
    获取mq总览
    """
    data = {}
    cl = pyrabbit2.Client("localhost:15672", "guest", "guest")
    overview = cl.get_overview()
    data = {
        "totals":{
            "ready": overview["queue_totals"]["messages_ready"],
            "unacked": overview["queue_totals"]["messages_unacknowledged"],
            "total": overview["queue_totals"]["messages"]
        },
        "global_totals": overview["object_totals"],
        "nodes": cl.get_nodes()
    }
    return JsonResponse({"result": True, "data": data})

@require_GET
@iam_intercept(StatisticsViewInpterceptor())
def get_mq_data(request):
    """
    获取mq数据
    """
    cl = pyrabbit2.Client("localhost:15672", "guest", "guest")
    data = {vhost: [{"vhost": vhost, "queue_name": queue["name"], "message_count": queue["messages"], "queue_state": queue["state"], "messages": cl.get_messages(vhost, queue["name"], count=queue["messages"], requeue=True)} for queue in cl.get_queues(vhost=vhost)] for vhost in cl.get_vhost_names()}
    return JsonResponse({"result": True, "data": data})
