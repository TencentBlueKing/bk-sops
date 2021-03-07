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

import logging
import datetime
import operator
from functools import reduce

from dateutil.relativedelta import relativedelta

from celery import task
from celery.decorators import periodic_task
from celery.schedules import crontab
from django.db import transaction
from django.db.models import Q

from pipeline.conf import default_settings
from pipeline.core.pipeline import Pipeline
from pipeline.engine import api, signals, states
from pipeline.engine.core import runtime, schedule
from pipeline.engine.health import zombie
from pipeline.engine.models import (
    NodeCeleryTask,
    NodeRelationship,
    PipelineProcess,
    ProcessCeleryTask,
    Status,
    Data,
    History,
    HistoryData,
    ScheduleService,
    MultiCallbackData,
    DataSnapshot,
    ScheduleCeleryTask,
    ProcessSnapshot,
    PipelineModel,
    SubProcessRelationship,
)
from pipeline.models import PipelineInstance

logger = logging.getLogger("celery")


@task(ignore_result=True)
def process_unfreeze(process_id):
    process = PipelineProcess.objects.get(id=process_id)
    if not process.is_alive:
        logger.warning("process(%s) is not alive, mission cancel." % process_id)
        return

    runtime.run_loop(process)


@task(ignore_result=True)
def start(process_id):
    process = PipelineProcess.objects.get(id=process_id)
    if not process.is_alive:
        logger.warning("process(%s) is not alive, mission cancel." % process_id)
        return

    pipeline_id = process.root_pipeline.id
    # try to run
    action_result = Status.objects.transit(pipeline_id, states.RUNNING, is_pipeline=True, start=True)
    if not action_result.result:
        logger.warning("can not start pipeline({}), message: {}".format(pipeline_id, action_result.message))
        return

    NodeRelationship.objects.build_relationship(pipeline_id, pipeline_id)

    runtime.run_loop(process)


@task(ignore_result=True)
def dispatch(child_id):
    process = PipelineProcess.objects.get(id=child_id)
    if not process.is_alive:
        logger.info("process(%s) is not alive, mission cancel." % child_id)
        return

    runtime.run_loop(process)


@task(ignore_result=True)
def process_wake_up(process_id, current_node_id=None, call_from_child=False):
    process = PipelineProcess.objects.get(id=process_id)
    if not process.is_alive:
        logger.warning("process(%s) is not alive, mission cancel." % process_id)
        return

    pipeline_id = process.root_pipeline.id
    if not call_from_child:
        # success_when_unchanged to deal with parallel wake up
        action_result = Status.objects.transit(
            pipeline_id, to_state=states.RUNNING, is_pipeline=True, unchanged_pass=True
        )
        if not action_result.result:
            # BLOCKED is a tolerant running state
            if action_result.extra.state != states.BLOCKED:
                logger.warning("can not start pipeline({}), message: {}".format(pipeline_id, action_result.message))
                return

    process.wake_up()
    if current_node_id:
        process.current_node_id = current_node_id

    runtime.run_loop(process)


@task(ignore_result=True)
def wake_up(process_id):
    process = PipelineProcess.objects.get(id=process_id)
    if not process.is_alive:
        logger.warning("process(%s) is not alive, mission cancel." % process_id)
        return

    process.wake_up()
    runtime.run_loop(process)


@task(ignore_result=True)
def batch_wake_up(process_id_list, pipeline_id):
    action_result = Status.objects.transit(pipeline_id, to_state=states.RUNNING, is_pipeline=True)
    if not action_result.result:
        logger.warning("can not start pipeline({}), message: {}".format(pipeline_id, action_result.message))
        return
    for process_id in process_id_list:
        task_id = wake_up.apply_async(args=[process_id]).id
        ProcessCeleryTask.objects.bind(process_id, task_id)


@task(ignore_result=True)
def wake_from_schedule(process_id, service_act_id):
    process = PipelineProcess.objects.get(id=process_id)
    process.wake_up()

    service_act = process.top_pipeline.node(service_act_id)
    process.current_node_id = service_act.next().id
    runtime.run_loop(process)


@task(ignore_result=True)
def service_schedule(process_id, schedule_id, data_id=None):
    schedule.schedule(process_id, schedule_id, data_id)


@task(ignore_result=True)
def node_timeout_check(node_id, version, root_pipeline_id):
    NodeCeleryTask.objects.destroy(node_id)
    state = Status.objects.state_for(node_id, version=version, may_not_exist=True)
    if not state or state != states.RUNNING:
        logger.warning("node {} {} timeout kill failed, node not exist or not in running".format(node_id, version))
        return

    action_result = api.forced_fail(node_id, kill=True, ex_data="node execution timeout")
    if action_result.result:
        signals.activity_failed.send(sender=Pipeline, pipeline_id=root_pipeline_id, pipeline_activity_id=node_id)
    else:
        logger.warning("node {} - {} timeout kill failed".format(node_id, version))


@periodic_task(run_every=(crontab(**default_settings.ENGINE_ZOMBIE_PROCESS_HEAL_CRON)), ignore_result=True)
def heal_zombie_process():
    logger.info("Zombie process heal start")

    healer = zombie.get_healer()

    try:
        healer.heal()
    except Exception:
        logger.exception("An error occurred when healing zombies")

    logger.info("Zombie process heal finish")


@periodic_task(run_every=(crontab(**default_settings.EXPIRED_TASK_CLEAN_CRON)), ignore_result=True)
def expired_tasks_clean():
    if not default_settings.EXPIRED_TASK_CLEAN:
        logger.info("EXPIRED_TASK_CLEAN switch off, won't clean expired tasks.")
        return
    logger.info("Expired tasks clean start")

    try:
        expired_create_time = datetime.date.today() - relativedelta(months=default_settings.TASK_EXPIRED_MONTH)
        pipeline_instance_ids = list(
            PipelineInstance.objects.filter(
                create_time__lte=expired_create_time, is_finished=True, is_revoked=False, is_expired=False
            ).values_list("instance_id", flat=True)[: default_settings.EXPIRED_TASK_CLEAN_NUM_LIMIT]
        )
        logger.info(
            "Clean expired tasks before {} with tasks number: {}, instance ids: {}".format(
                expired_create_time, len(pipeline_instance_ids), ",".join(pipeline_instance_ids)
            )
        )

        total_process_nodes = []
        for instance_id in pipeline_instance_ids:
            process_nodes = NodeRelationship.objects.filter(ancestor_id=instance_id).values_list(
                "descendant_id", flat=True
            )
            process_nodes = list(set(process_nodes))
            total_process_nodes += process_nodes

        pipeline_process = PipelineProcess.objects.filter(root_pipeline_id__in=pipeline_instance_ids)
        pipeline_process_ids = pipeline_process.values_list("id", flat=True)
        subprocess_relationship = SubProcessRelationship.objects.filter(process_id__in=pipeline_process_ids)
        process_snapshot_ids = pipeline_process.values_list("snapshot__id", flat=True)
        process_snapshot = ProcessSnapshot.objects.filter(id__in=process_snapshot_ids)
        pipeline_model = PipelineModel.objects.filter(process_id__in=pipeline_process_ids)
        process_celery_task = ProcessCeleryTask.objects.filter(process_id__in=pipeline_process_ids)
        schedule_service = ScheduleService.objects.filter(process_id__in=pipeline_process_ids)
        schedule_service_ids = schedule_service.values_list("id", flat=True)
        multi_callback_data = MultiCallbackData.objects.filter(schedule_id__in=schedule_service_ids)
        node_relationship = NodeRelationship.objects.filter(
            Q(ancestor_id__in=total_process_nodes) | Q(descendant_id__in=total_process_nodes)
        )
        node_celery_tasks = NodeCeleryTask.objects.filter(node_id__in=total_process_nodes)
        status = Status.objects.filter(id__in=total_process_nodes)
        data = Data.objects.filter(id__in=total_process_nodes)
        data_snapshot_prefixes = [Q(key__startswith=process_node) for process_node in total_process_nodes]
        data_snapshot = DataSnapshot.objects.filter(reduce(operator.or_, data_snapshot_prefixes, Q(key=None)))
        schedule_celery_task_prefixes = [
            Q(schedule_id__startswith=process_node) for process_node in total_process_nodes
        ]
        schedule_celery_task = ScheduleCeleryTask.objects.filter(
            reduce(operator.or_, schedule_celery_task_prefixes, Q(schedule_id=None))
        )
        history = History.objects.filter(identifier__in=total_process_nodes).only("data")
        history_data_ids = history.values_list("data__id", flat=True)
        history_data = HistoryData.objects.filter(id__in=history_data_ids)

        with transaction.atomic():
            schedule_service.delete()
            multi_callback_data.delete()
            history.delete()
            history_data.delete()
            data.delete()
            status.delete()
            node_celery_tasks.delete()
            schedule_celery_task.delete()
            data_snapshot.delete()
            node_relationship.delete()
            subprocess_relationship.delete()
            pipeline_process.delete()
            process_snapshot.delete()
            pipeline_model.delete()
            process_celery_task.delete()
            PipelineInstance.objects.filter(instance_id__in=pipeline_instance_ids).update(is_expired=True)
    except Exception as e:
        logger.exception("An error occurred when clean expired tasks: {}".format(e))

    logger.info("Expired tasks clean finish")
