# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import datetime
import logging
import traceback

import pytz
from celery import task
from django.utils import timezone

from pipeline.contrib.periodic_task import signals
from pipeline.contrib.periodic_task.models import PeriodicTask, PeriodicTaskHistory
from pipeline.engine.models import FunctionSwitch
from pipeline.models import PipelineInstance

logger = logging.getLogger("celery")


@task(ignore_result=True)
def periodic_task_start(*args, **kwargs):
    try:
        periodic_task = PeriodicTask.objects.get(id=kwargs["period_task_id"])
    except PeriodicTask.DoesNotExist:
        # task has been deleted
        return

    if FunctionSwitch.objects.is_frozen():
        PeriodicTaskHistory.objects.record_schedule(
            periodic_task=periodic_task,
            pipeline_instance=None,
            ex_data="engine is frozen, can not start task",
            start_success=False,
        )
        return

    try:
        tz = periodic_task.celery_task.crontab.timezone
        now = datetime.datetime.now(tz=pytz.utc).astimezone(tz)
        instance, _ = PipelineInstance.objects.create_instance(
            template=periodic_task.template,
            exec_data=periodic_task.execution_data,
            spread=kwargs.get("spread", True),
            name="{}_{}".format(periodic_task.name[:113], now.strftime("%Y%m%d%H%M%S")),
            creator=periodic_task.creator,
            description="periodic task instance",
        )

        signals.pre_periodic_task_start.send(
            sender=PeriodicTask, periodic_task=periodic_task, pipeline_instance=instance
        )

        result = instance.start(
            periodic_task.creator, check_workers=False, priority=periodic_task.priority, queue=periodic_task.queue,
        )
    except Exception:
        et = traceback.format_exc()
        logger.error(et)
        PeriodicTaskHistory.objects.record_schedule(
            periodic_task=periodic_task, pipeline_instance=None, ex_data=et, start_success=False,
        )
        return

    if not result.result:
        PeriodicTaskHistory.objects.record_schedule(
            periodic_task=periodic_task, pipeline_instance=None, ex_data=result.message, start_success=False,
        )
        return

    periodic_task.total_run_count += 1
    periodic_task.last_run_at = timezone.now()
    periodic_task.save()
    signals.post_periodic_task_start.send(sender=PeriodicTask, periodic_task=periodic_task, pipeline_instance=instance)

    PeriodicTaskHistory.objects.record_schedule(periodic_task=periodic_task, pipeline_instance=instance, ex_data="")
