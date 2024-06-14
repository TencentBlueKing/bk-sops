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

from django.db import connection
from django.http import JsonResponse
from django.views.decorators.http import require_GET

from gcloud.iam_auth.intercept import iam_intercept
from gcloud.iam_auth.view_interceptors.statistics import StatisticsViewInpterceptor


@require_GET
@iam_intercept(StatisticsViewInpterceptor())
def get_failed_task(request):
    """
    获取失败任务
    """
    limit = int(request.GET.get("limit", 100))
    offset = int(request.GET.get("offset", 0))
    failed_sql = f"""SELECT
            tt.id AS task_id,
            cp.NAME AS project_name,
            pp.NAME AS task_name
        FROM
            `taskflow3_taskflowinstance` AS tt,
            `core_project` AS cp,
            `pipeline_pipelineinstance` AS pp,
            `eri_state` AS es
        WHERE
            pp.instance_id = es.root_id
            AND tt.pipeline_instance_id = pp.id
            AND tt.project_id = cp.id
            AND pp.is_deleted = 0
            AND pp.is_expired = 0
            AND pp.is_finished = 0
            AND pp.is_revoked = 0
            AND pp.is_started = 1
            AND es.NAME = "FAILED"
        ORDER BY
            pp.id DESC
        LIMIT
            {offset},{limit}"""
    with connection.cursor() as cursor:
        cursor.execute(failed_sql)
        failed_tasks = [
            {"task_id": item[0], "project_name": item[1], "task_name": item[2]} for item in cursor.fetchall()
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

    def get_data(offset, limit):
        failed_sql = f"""SELECT
                pp.id
            FROM
                `pipeline_pipelineinstance` AS pp,
                `eri_state` AS es
            WHERE
                pp.instance_id = es.root_id
                AND pp.is_deleted = 0
                AND pp.is_expired = 0
                AND pp.is_finished = 0
                AND pp.is_revoked = 0
                AND pp.is_started = 1
                AND es.NAME = "FAILED"
            ORDER BY
                pp.id DESC
            LIMIT
                {offset}, {limit}"""

        with connection.cursor() as cursor:
            cursor.execute(failed_sql)
            failed_task_ids = [item[0] for item in cursor.fetchall()]
        no_failed_sql = f"""SELECT
                pp.id,
                tt.id AS task_id,
                cp.NAME AS project_name,
                pp.NAME AS task_name
            FROM
                `taskflow3_taskflowinstance` AS tt,
                `core_project` AS cp,
                `pipeline_pipelineinstance` AS pp
            WHERE
                tt.pipeline_instance_id = pp.id
                AND tt.project_id = cp.id
                AND pp.is_deleted = 0
                AND pp.is_expired = 0
                AND pp.is_finished = 0
                AND pp.is_revoked = 0
                AND pp.is_started = 1
            ORDER BY
                pp.id DESC
            LIMIT
                {offset}, {limit}"""
        with connection.cursor() as cursor:
            cursor.execute(no_failed_sql)
            no_failed_tasks = [
                {"task_id": item[1], "project_name": item[2], "task_name": item[3]}
                for item in cursor.fetchall()
                if item[0] not in failed_task_ids
            ]
        return no_failed_tasks

    no_failed_tasks = []
    for i in range(offset, 5 * limit + offset, limit):
        if len(no_failed_tasks) < limit:
            no_failed_tasks.extend(get_data(i, limit))
    return JsonResponse({"result": True, "data": no_failed_tasks})


@require_GET
@iam_intercept(StatisticsViewInpterceptor())
def get_schedule_times(request):
    """
    获取调度次数
    """
    limit = int(request.GET.get("limit", 100))
    offset = int(request.GET.get("offset", 0))
    schedule_times_sql = f"""SELECT
            pp.id,
            pp.creator,
            esc.schedule_times
        FROM
            eri_schedule AS esc,
            eri_state AS es,
            pipeline_pipelineinstance AS pp
        WHERE
            esc.node_id = es.node_id
            AND es.root_id = pp.instance_id
            AND esc.scheduling = 0
        ORDER BY
            esc.schedule_times DESC
        LIMIT
            {offset},{limit}"""
    with connection.cursor() as cursor:
        cursor.execute(schedule_times_sql)
        schedule_times = [{"id": item[0], "creator": item[1], "schedule_times": item[2]} for item in cursor.fetchall()]
    return JsonResponse({"result": True, "data": schedule_times})
