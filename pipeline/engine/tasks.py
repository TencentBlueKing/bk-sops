# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

from __future__ import absolute_import
import logging

from celery import task

from pipeline.engine import states
from pipeline.engine.core import runtime, schedule
from pipeline.engine.models import PipelineProcess, Status, NodeRelationship, ProcessCeleryTask

logger = logging.getLogger('celery')


@task(ignore_result=True)
def process_unfreeze(process_id):
    process = PipelineProcess.objects.get(id=process_id)
    if not process.is_alive:
        logger.info('process(%s) is not alive, mission cancel.' % process_id)
        return

    runtime.run_loop(process)


@task(ignore_result=True)
def start(process_id):
    process = PipelineProcess.objects.get(id=process_id)
    if not process.is_alive:
        logger.info('process(%s) is not alive, mission cancel.' % process_id)
        return

    pipeline_id = process.root_pipeline.id
    # try to run
    if not Status.objects.transit(pipeline_id, states.RUNNING, is_pipeline=True, start=True):
        logger.info('can not start pipeline(%s), perhaps state of the pipeline has been changed' % pipeline_id)
        return

    NodeRelationship.objects.build_relationship(pipeline_id, pipeline_id)

    runtime.run_loop(process)


@task(ignore_result=True)
def dispatch(child_id):
    process = PipelineProcess.objects.get(id=child_id)
    if not process.is_alive:
        logger.info('process(%s) is not alive, mission cancel.' % child_id)
        return

    runtime.run_loop(process)


@task(ignore_result=True)
def process_wake_up(process_id, current_node_id=None, call_from_child=False):
    process = PipelineProcess.objects.get(id=process_id)
    if not process.is_alive:
        logger.info('process(%s) is not alive, mission cancel.' % process_id)
        return

    pipeline_id = process.root_pipeline.id
    if not call_from_child:
        if not Status.objects.transit(pipeline_id, to_state=states.RUNNING, is_pipeline=True):
            logger.info('can not start pipeline(%s), perhaps state of the pipeline has been changed' % pipeline_id)
            return
    else:
        process.sync_with_children()

    process.wake_up()
    if current_node_id:
        process.current_node_id = current_node_id

    runtime.run_loop(process)


@task(ignore_result=True)
def wake_up(process_id):
    process = PipelineProcess.objects.get(id=process_id)
    if not process.is_alive:
        logger.info('process(%s) is not alive, mission cancel.' % process_id)
        return

    process.wake_up()
    runtime.run_loop(process)


@task(ignore_result=True)
def batch_wake_up(process_id_list, pipeline_id):
    if not Status.objects.transit(pipeline_id, to_state=states.RUNNING, is_pipeline=True):
        logger.info('can not start pipeline(%s), perhaps state of the pipeline has been changed' % pipeline_id)
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
def service_schedule(process_id, schedule_id):
    schedule.schedule(process_id, schedule_id)
