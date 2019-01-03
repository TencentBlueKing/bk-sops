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
import traceback
from collections import namedtuple

from pipeline.core.flow import activity, gateway, event
from pipeline.engine.core.data import hydrate_node_data, hydrate_data
from pipeline.engine import states, signals
from pipeline.engine.models import Status, Data, PipelineProcess, ScheduleService
from django_signal_valve import valve

logger = logging.getLogger('celery')
HandleResult = namedtuple('HandleResult', 'next_node should_return should_sleep')


# handlers

def service_activity_handler(process, service_act):
    success = False
    exception_occurred = False

    # hydrate inputs
    hydrate_node_data(service_act)

    # execute service
    try:
        success = service_act.execute(process.root_pipeline.data)
    except Exception as e:
        if service_act.error_ignorable:
            # ignore exception
            success = True
            exception_occurred = True
            service_act.ignore_error()
        else:
            # send activity error signal
            valve.send(signals, 'activity_failed', sender=process.root_pipeline,
                       pipeline_id=process.root_pipeline.id,
                       pipeline_activity_id=service_act.id)
        ex_data = traceback.format_exc(e)
        service_act.data.set_outputs('ex_data', ex_data)
        logger.error(ex_data)

    # process result
    if success is False:
        ex_data = service_act.data.get_one_of_outputs('ex_data')
        Status.objects.fail(service_act, ex_data)
        try:
            service_act.failure_handler(process.root_pipeline.data)
            # send activity error signal
            valve.send(signals, 'activity_failed', sender=process.root_pipeline,
                       pipeline_id=process.root_pipeline.id,
                       pipeline_activity_id=service_act.id)
        except Exception as e:
            logger.error('failure_handler(%s) failed: %s' % (service_act.id, traceback.format_exc(e)))
        return HandleResult(next_node=None, should_return=False, should_sleep=True)
    else:
        if service_act.need_schedule() and not exception_occurred:
            # set schedule
            version = Status.objects.get(id=service_act.id).version
            ScheduleService.objects.set_schedule(service_act.id, service_act=service_act.shell(),
                                                 process_id=process.id, version=version,
                                                 parent_data=process.top_pipeline.data)
            return HandleResult(next_node=None, should_return=True, should_sleep=True)
        process.top_pipeline.context().extract_output(service_act)
        error_ignorable = not service_act.get_result_bit()
        if not Status.objects.finish(service_act, error_ignorable):
            # has been forced failed
            return HandleResult(next_node=None, should_return=False, should_sleep=True)
        return HandleResult(next_node=service_act.next(), should_return=False, should_sleep=False)


def subprocess_handler(process, subprocess_act):
    # hydrate data
    hydrate_node_data(subprocess_act)

    # context injection
    data = subprocess_act.pipeline.data
    context = subprocess_act.pipeline.context()
    for k, v in data.get_inputs().iteritems():
        context.set_global_var(k, v)

    hydrated = hydrate_data(context.variables)
    context.update_global_var(hydrated)

    sub_pipeline = subprocess_act.pipeline
    process.push_pipeline(sub_pipeline, is_subprocess=True)
    return HandleResult(next_node=sub_pipeline.start_event(), should_return=False, should_sleep=False)


def parallel_gateway_handler(process, parallel_gateway):
    targets = parallel_gateway.outgoing.all_target_node()
    children = []

    for target in targets:
        try:
            child = PipelineProcess.objects.fork_child(parent=process, current_node_id=target.id,
                                                       destination_id=parallel_gateway.converge_gateway_id)
        except Exception as e:
            ex_data = traceback.format_exc(e)
            logger.error(ex_data)
            Status.objects.fail(parallel_gateway, ex_data)
            return HandleResult(next_node=None, should_return=True, should_sleep=True)

        children.append(child)

    process.join(children)

    Status.objects.finish(parallel_gateway)

    return HandleResult(next_node=None, should_return=True, should_sleep=True)


def empty_end_event_handler(process, end_event):
    pipeline = process.pop_pipeline()
    if process.pipeline_stack:
        # pop subprocess and return to top of stack
        pipeline.spec.context.write_output(pipeline)
        Status.objects.finish(end_event)
        sub_process_node = process.top_pipeline.node(pipeline.id)
        Status.objects.finish(sub_process_node)
        pipeline.context().clear()
        # extract subprocess output
        process.top_pipeline.context().extract_output(sub_process_node)
        return HandleResult(next_node=sub_process_node.next(), should_return=False, should_sleep=False)
    else:
        with Status.objects.lock(pipeline.id):
            # save data and destroy process
            pipeline.spec.context.write_output(pipeline)
            Data.objects.write_node_data(pipeline)
            Status.objects.finish(end_event)

            Status.objects.transit(pipeline.id, to_state=states.FINISHED, is_pipeline=True)
            # PipelineInstance.objects.set_finished(process.root_pipeline.id)
            end_event.pipeline_finish(process.root_pipeline.id)
            pipeline.context().clear()
            process.destroy()
            return HandleResult(next_node=None, should_return=True, should_sleep=False)


def empty_start_event_handler(process, start_event):
    Status.objects.finish(start_event)
    return HandleResult(next_node=start_event.next(), should_return=False, should_sleep=False)


def exclusive_gateway_handler(process, ex_gateway):
    try:
        hydrate_context = hydrate_data(process.top_pipeline.context().variables)
        next_node = ex_gateway.next(hydrate_context)
    except Exception as e:
        ex_data = traceback.format_exc(e)
        logger.error(ex_data)
        Status.objects.fail(ex_gateway, ex_data=ex_data)
        return HandleResult(next_node=None, should_return=True, should_sleep=True)
    Status.objects.finish(ex_gateway)
    return HandleResult(next_node=next_node, should_return=False, should_sleep=False)


def converge_gateway_handler(process, converge_gateway):
    Status.objects.finish(converge_gateway)
    return HandleResult(next_node=converge_gateway.next(), should_return=False, should_sleep=False)


FLOW_NODE_HANDLERS = {
    event.EmptyStartEvent: empty_start_event_handler,
    event.EmptyEndEvent: empty_end_event_handler,
    activity.ServiceActivity: service_activity_handler,
    activity.SubProcess: subprocess_handler,
    gateway.ExclusiveGateway: exclusive_gateway_handler,
    gateway.ParallelGateway: parallel_gateway_handler,
    gateway.ConvergeGateway: converge_gateway_handler
}
