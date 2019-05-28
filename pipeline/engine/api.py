# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from __future__ import absolute_import
import functools
import time

from redis.exceptions import ConnectionError as RedisConnectionError

from pipeline.core.flow.activity import ServiceActivity
from pipeline.core.flow.gateway import ExclusiveGateway, ParallelGateway
from pipeline.engine.core.api import workers
from pipeline.engine import states, exceptions
from pipeline.engine.models import (
    Status,
    PipelineModel,
    PipelineProcess,
    NodeRelationship,
    ScheduleService,
    Data,
    SubProcessRelationship,
    ProcessCeleryTask,
    History,
    FunctionSwitch,
)
from pipeline.engine.utils import calculate_elapsed_time, ActionResult
from pipeline.utils import uniqid

from django.db import transaction


def _node_existence_check(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        id_from_kwargs = kwargs.get('node_id')
        node_id = id_from_kwargs if id_from_kwargs else args[0]
        try:
            Status.objects.get(id=node_id)
        except Status.DoesNotExist:
            return ActionResult(result=False, message='node not exists or not be executed yet')
        return func(*args, **kwargs)

    return wrapper


def _frozen_check(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if FunctionSwitch.objects.is_frozen():
            return ActionResult(result=False, message='engine is frozen, can not perform operation')

        return func(*args, **kwargs)

    return wrapper


def _worker_check(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if kwargs.get('check_workers', True):
            try:
                if not workers():
                    return ActionResult(result=False, message='can not find celery workers, please check worker status')
            except exceptions.RabbitMQConnectionError as e:
                return ActionResult(result=False, message='celery worker status check failed with message: %s, '
                                                          'check rabbitmq status please' % e.message)
            except RedisConnectionError:
                return ActionResult(result=False, message='redis connection error, check redis status please')

        return func(*args, **kwargs)

    return wrapper


@_worker_check
@_frozen_check
def start_pipeline(pipeline_instance, check_workers=True):
    """
    start a pipeline
    :param pipeline_instance:
    :return:
    """

    Status.objects.prepare_for_pipeline(pipeline_instance)
    process = PipelineProcess.objects.prepare_for_pipeline(pipeline_instance)
    PipelineModel.objects.prepare_for_pipeline(pipeline_instance, process)

    PipelineModel.objects.pipeline_ready(process_id=process.id)

    return ActionResult(result=True, message='success')


@_frozen_check
def pause_pipeline(pipeline_id):
    """
    pause a running pipeline
    :param pipeline_id:
    :return:
    """

    return Status.objects.transit(id=pipeline_id, to_state=states.SUSPENDED, is_pipeline=True, appoint=True)


@_worker_check
@_frozen_check
def resume_pipeline(pipeline_id):
    """
    resume a pipeline from suspended
    :param pipeline_id:
    :return:
    """

    action_result = Status.objects.transit(id=pipeline_id, to_state=states.READY, is_pipeline=True, appoint=True)
    if not action_result.result:
        return action_result

    process = PipelineModel.objects.get(id=pipeline_id).process
    to_be_waked = []
    _get_process_to_be_waked(process, to_be_waked)
    PipelineProcess.objects.batch_process_ready(process_id_list=to_be_waked, pipeline_id=pipeline_id)

    return action_result


@_frozen_check
def revoke_pipeline(pipeline_id):
    """
    revoke a pipeline
    :param pipeline_id:
    :return:
    """

    action_result = Status.objects.transit(id=pipeline_id, to_state=states.REVOKED, is_pipeline=True, appoint=True)
    if not action_result.result:
        return action_result

    process = PipelineModel.objects.get(id=pipeline_id).process
    process.revoke_subprocess()
    process.destroy_all()

    return action_result


@_frozen_check
def pause_node_appointment(node_id):
    """
    make a appointment to pause a node
    :param node_id:
    :return:
    """

    return Status.objects.transit(id=node_id, to_state=states.SUSPENDED, appoint=True)


@_worker_check
@_frozen_check
@_node_existence_check
def resume_node_appointment(node_id):
    """
    make a appointment to resume a node
    :param node_id:
    :return:
    """

    qs = PipelineProcess.objects.filter(current_node_id=node_id, is_sleep=True)
    if qs.exists():
        # a process had sleep caused by pause reservation
        action_result = Status.objects.transit(id=node_id, to_state=states.READY, appoint=True)
        if not action_result.result:
            return action_result

        process = qs.first()
        Status.objects.recover_from_block(process.root_pipeline.id, process.subprocess_stack)
        PipelineProcess.objects.process_ready(process_id=process.id)
        return ActionResult(result=True, message='success')

    processing_sleep = SubProcessRelationship.objects.get_relate_process(subprocess_id=node_id)
    if processing_sleep.exists():
        action_result = Status.objects.transit(id=node_id, to_state=states.RUNNING, appoint=True, is_pipeline=True)
        if not action_result.result:
            return action_result
        # processes had sleep caused by subprocess pause
        root_pipeline_id = processing_sleep.first().root_pipeline_id

        process_can_be_waked = filter(lambda p: p.can_be_waked(), processing_sleep)
        can_be_waked_ids = map(lambda p: p.id, process_can_be_waked)

        # get subprocess id which should be transited
        subprocess_to_be_transit = set()
        for process in process_can_be_waked:
            _, subproc_above = process.subproc_sleep_check()
            for subproc in subproc_above:
                subprocess_to_be_transit.add(subproc)

        Status.objects.recover_from_block(root_pipeline_id, subprocess_to_be_transit)
        PipelineProcess.objects.batch_process_ready(process_id_list=can_be_waked_ids,
                                                    pipeline_id=root_pipeline_id)
        return ActionResult(result=True, message='success')

    return ActionResult(result=False, message='node not exists or not be executed yet')


@_worker_check
@_frozen_check
@_node_existence_check
def retry_node(node_id, inputs=None):
    """
    retry a node
    :param node_id:
    :param inputs:
    :return:
    """

    try:
        PipelineProcess.objects.get(current_node_id=node_id)
    except PipelineProcess.DoesNotExist:  # can not retry subprocess
        return ActionResult(result=False, message='can\'t not retry a subprocess or this process has been revoked')

    process = PipelineProcess.objects.get(current_node_id=node_id)

    # try to get next
    node = process.top_pipeline.node(node_id)
    if not (isinstance(node, ServiceActivity) or isinstance(node, ParallelGateway)):
        return ActionResult(result=False, message='can\'t retry this type of node')

    if hasattr(node, 'can_retry') and not node.can_retry:
        return ActionResult(result=False, message='the node is set to not be retried, try skip it please.')

    action_result = Status.objects.retry(process, node, inputs)
    if not action_result.result:
        return action_result

    # wake up process
    PipelineProcess.objects.process_ready(process_id=process.id)

    return action_result


@_worker_check
@_frozen_check
@_node_existence_check
def skip_node(node_id):
    """
    skip a node
    :param node_id:
    :return:
    """

    try:
        process = PipelineProcess.objects.get(current_node_id=node_id)
    except PipelineProcess.DoesNotExist:  # can not skip subprocess
        return ActionResult(result=False, message='can\'t not skip a subprocess or this process has been revoked')

    # try to get next
    node = process.top_pipeline.node(node_id)
    if not isinstance(node, ServiceActivity):
        return ActionResult(result=False, message='can\'t skip this type of node')

    if not node.skippable:
        return ActionResult(result=False, message='this node can not be skipped')

    # skip and write result bit
    action_result = Status.objects.skip(process, node)
    if not action_result.result:
        return action_result

    next_node_id = node.next().id

    # extract outputs and wake up process
    process.top_pipeline.context.extract_output(node)
    process.save()
    PipelineProcess.objects.process_ready(process_id=process.id, current_node_id=next_node_id)

    return action_result


@_worker_check
@_frozen_check
@_node_existence_check
def skip_exclusive_gateway(node_id, flow_id):
    """
    skip a failed exclusive gateway and appoint the flow to be pushed
    :param node_id:
    :param flow_id:
    :return:
    """

    try:
        process = PipelineProcess.objects.get(current_node_id=node_id)
    except PipelineProcess.DoesNotExist:
        return ActionResult(result=False,
                            message='invalid operation, this gateway is finished or pipeline have been revoked')

    exclusive_gateway = process.top_pipeline.node(node_id)

    if not isinstance(exclusive_gateway, ExclusiveGateway):
        return ActionResult(result=False, message='invalid operation, this node is not a exclusive gateway')

    next_node_id = exclusive_gateway.target_for_sequence_flow(flow_id).id

    action_result = Status.objects.skip(process, exclusive_gateway)
    if not action_result.result:
        return action_result

    # wake up process
    PipelineProcess.objects.process_ready(process_id=process.id, current_node_id=next_node_id)

    return action_result


def get_status_tree(node_id, max_depth=1):
    """
    get state and children states for a node
    :param node_id:
    :param max_depth:
    :return:
    """
    rel_qs = NodeRelationship.objects.filter(ancestor_id=node_id, distance__lte=max_depth)
    if not rel_qs.exists():
        raise exceptions.InvalidOperationException('node(%s) does not exist, may have not by executed' % node_id)
    descendants = map(lambda rel: rel.descendant_id, rel_qs)
    # remove root node
    descendants.remove(node_id)

    rel_qs = NodeRelationship.objects.filter(descendant_id__in=descendants, distance=1)
    targets = map(lambda rel: rel.descendant_id, rel_qs)

    root_status = Status.objects.filter(id=node_id).values().first()
    root_status['elapsed_time'] = calculate_elapsed_time(root_status['started_time'], root_status['archived_time'])
    status_map = {node_id: root_status}
    status_qs = Status.objects.filter(id__in=targets).values()
    for status in status_qs:
        status['elapsed_time'] = calculate_elapsed_time(status['started_time'], status['archived_time'])
        status_map[status['id']] = status

    relationships = [(s.ancestor_id, s.descendant_id) for s in rel_qs]
    for (parent_id, child_id) in relationships:
        if parent_id not in status_map:
            return

        parent_status = status_map[parent_id]
        child_status = status_map[child_id]
        child_status.setdefault('children', {})

        parent_status.setdefault('children', {}).setdefault(child_id, child_status)

    return status_map[node_id]


@_worker_check
@_frozen_check
def activity_callback(activity_id, callback_data):
    """
    callback a schedule node
    :param activity_id:
    :param callback_data:
    :return:
    """

    version = Status.objects.version_for(activity_id)
    times = 0

    # it's possible that ScheduleService is not be set when callback make
    while times < 3:
        try:
            service = ScheduleService.objects.schedule_for(activity_id, version)
            break
        except ScheduleService.DoesNotExist as e:
            times += 1
            time.sleep(times)
            if times >= 3:
                raise e

    try:
        process_id = PipelineProcess.objects.get(current_node_id=activity_id).id
    except PipelineProcess.DoesNotExist:
        return ActionResult(result=False,
                            message='invalid operation, this node is finished or pipeline have been revoked')

    if service.is_finished:
        raise exceptions.InvalidOperationException('activity(%s) callback already finished' % activity_id)
    service.callback(callback_data, process_id)
    return ActionResult(result=True, message='success')


def get_inputs(node_id):
    """
    get inputs data for a node
    :param node_id:
    :return:
    """
    return Data.objects.get(id=node_id).inputs


def get_outputs(node_id):
    """
    get outputs data for a node
    :param node_id:
    :return:
    """
    data = Data.objects.get(id=node_id)
    return {
        'outputs': data.outputs,
        'ex_data': data.ex_data
    }


def get_activity_histories(node_id):
    """
    get get_activity_histories data for a node
    :param node_id:
    :return:
    """
    return History.objects.get_histories(node_id)


def get_single_state(node_id):
    """
    get state for single node
    :param node_id:
    :return:
    """
    s = Status.objects.get(id=node_id)
    return {
        'state': s.state,
        'started_time': s.started_time,
        'finished_time': s.archived_time,
        'retry': s.retry,
        'skip': s.skip
    }


@_frozen_check
@_node_existence_check
def forced_fail(node_id, kill=False, ex_data=''):
    """
    forced fail a node
    :param node_id:
    :param kill:
    :param ex_data:
    :return:
    """

    try:
        process = PipelineProcess.objects.get(current_node_id=node_id)
    except PipelineProcess.DoesNotExist:
        return ActionResult(result=False,
                            message='invalid operation, this node is finished or pipeline have been revoked')

    node = process.top_pipeline.node(node_id)
    if not isinstance(node, ServiceActivity):
        return ActionResult(result=False, message='can\'t not forced fail this type of node')

    action_result = Status.objects.transit(node_id, to_state=states.FAILED)
    if not action_result.result:
        return action_result

    try:
        node.failure_handler(process.root_pipeline.data)
    except Exception:
        pass

    with transaction.atomic():
        s = Status.objects.get(id=node.id)
        ScheduleService.objects.delete_schedule(s.id, s.version)
        Data.objects.forced_fail(node_id, ex_data)
        ProcessCeleryTask.objects.revoke(process.id, kill)
        process.sleep(adjust_status=True)
        s.version = uniqid.uniqid()
        s.save()

    return ActionResult(result=True, message='success')


def _get_process_to_be_waked(process, to_be_waked):
    if process.can_be_waked():
        to_be_waked.append(process.id)
    elif process.children:
        for child_id in process.children:
            child = PipelineProcess.objects.get(id=child_id)
            _get_process_to_be_waked(child, to_be_waked)
