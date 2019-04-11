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

from modbpm.core import AbstractProcess, AbstractTask
from modbpm.core.data.base import get_data_source

from pipeline.core.flow.activity import ServiceActivity, SubProcess
from pipeline.core.flow.event import EmptyStartEvent, EmptyEndEvent
from pipeline.core.flow.gateway import ExclusiveGateway, ParallelGateway, \
    ConvergeGateway
from pipeline.models import PipelineInstance
from pipeline.core.data import var
from pipeline import exceptions


class PipelineProcess(AbstractProcess):
    def on_start(self, pipeline, instance_id=None):
        end_event_id = pipeline.end_event.id
        _auto_loop_node(self, pipeline.start_event, end_event_id, pipeline, instance_id)
        self.start(act=EmptyEndEventTask, identifier_code=end_event_id)(instance_id)
        # write output
        pipeline.spec.context.write_output(pipeline)
        # clear context: break circle reference
        pipeline.spec.context.clear()
        self.finish(data=pipeline.data.get_outputs())


class SerialProcess(AbstractProcess):
    def on_start(self, node, end_id, pipeline):
        _auto_loop_node(self, node, end_id, pipeline)
        self.finish()


class ServiceActivityTask(AbstractTask):
    def on_start(self, service_act, parent_data):
        if service_act.execute(parent_data):
            if not service_act.need_schedule():
                self._finish(service_act, parent_data)

            data_source = get_data_source(self._get_model())
            data_source.set('service_act', service_act)
            data_source.set('parent_data', parent_data)
            self.set_default_scheduler(self.on_schedule)
        else:
            self.finish(status_code=2)

    def on_schedule(self):
        data_source = get_data_source(self._get_model())
        service_act = data_source.get('service_act')
        parent_data = data_source.get('parent_data')

        schedule_result = service_act.schedule(parent_data)
        if not schedule_result:
            self.finish(status_code=2)
        if service_act.is_schedule_done():
            self._finish(service_act, parent_data)

        data_source.set('service_act', service_act)
        data_source.set('parent_data', parent_data)

    def _finish(self, service_act, parent_data):
        data = {
            'data': service_act.data.get_outputs(),
            'parent_data': parent_data.get_outputs()
        }
        self.finish(data=data)


class EmptyTask(AbstractTask):
    def on_start(self):
        self.finish()


class EmptyStartEventTask(EmptyTask):
    def on_start(self, instance_id=None):
        if instance_id:
            PipelineInstance.objects.set_started(instance_id)
        self.finish()


class EmptyEndEventTask(EmptyTask):
    def on_start(self, instance_id=None):
        if instance_id:
            PipelineInstance.objects.set_finished(instance_id)
        self.finish()


class EmptyExclusiveGateway(EmptyTask):
    pass


class EmptyParallelGateway(EmptyTask):
    pass


class EmptyConvergeGateway(EmptyTask):
    pass


class SkipUsingTask(AbstractTask):
    def on_start(self, *args, **kwargs):
        self.finish()


def _data_transfer(origin, target_data):
    for key, value in origin.items():
        target_data.set_outputs(key, value)


def _hydrate_data(act):
    data = act.data
    inputs = data.get_inputs()
    hydrated = {}
    for k, v in inputs.items():
        if issubclass(v.__class__, var.Variable):
            hydrated[k] = v.get()
    data.get_inputs().update(hydrated)


def _context_injection(data, context):
    for k, v in data.get_inputs().items():
        context.set_global_var(k, v)
    hydrated = {}
    for k, v in context.variables.items():
        if issubclass(v.__class__, var.Variable):
            hydrated[k] = v.get()
    context.update_global_var(hydrated)


def _auto_loop_node(parent_act, enter_node, exit_node_id, pipeline, instance_id=None):
    current_node = enter_node

    while current_node.id != exit_node_id:
        if isinstance(current_node, ServiceActivity):
            # hydrate all lazy variables
            try:
                _hydrate_data(current_node)
            except Exception as e:
                raise exceptions.VariableHydrateException(e.message)

            handler = parent_act.start(
                act=ServiceActivityTask,
                identifier_code=current_node.id
            )(current_node, pipeline.data)
            outputs = handler.get()

            # transfer data
            if outputs:
                _data_transfer(outputs['data'], current_node.data)
                _data_transfer(outputs['parent_data'], pipeline.data)
            # extract output
            pipeline.spec.context.extract_output(current_node)
            current_node = current_node.next()

        elif isinstance(current_node, SubProcess):
            # inject variable to context
            _hydrate_data(current_node)
            _context_injection(current_node.data, current_node.pipeline.context)

            handler = parent_act.start(
                act=PipelineProcess,
                identifier_code=current_node.id
            )(current_node.pipeline)
            outputs = handler.get()

            # transfer data
            if outputs:
                _data_transfer(outputs, current_node.data)

            # extract output
            pipeline.spec.context.extract_output(current_node)
            current_node = current_node.next()

        elif isinstance(current_node, EmptyStartEvent):
            parent_act.start(act=EmptyStartEventTask, identifier_code=current_node.id)(instance_id)
            current_node = current_node.next()

        elif isinstance(current_node, EmptyEndEvent):
            parent_act.start(act=EmptyEndEventTask, identifier_code=current_node.id)(instance_id)
            current_node = current_node.next()

        elif isinstance(current_node, ExclusiveGateway):
            # determine next node
            parent_act.start(act=EmptyExclusiveGateway, identifier_code=current_node.id)()
            current_node = current_node.next(data=pipeline.spec.context.variables)

        elif isinstance(current_node, ParallelGateway):
            parent_act.start(act=EmptyParallelGateway, identifier_code=current_node.id)()
            current_node = _into_parallel_gateway(parent_act, current_node,
                                                  pipeline)

        elif isinstance(current_node, ConvergeGateway):
            parent_act.start(act=EmptyConvergeGateway, identifier_code=current_node.id)()
            current_node = current_node.next()

    return current_node


def _into_parallel_gateway(parent_act, gateway, pipeline):
    all_target = gateway.outgoing.all_target_node()
    with parent_act.run_in_parallel():
        for target in all_target:
            parent_act.start(SerialProcess)(target,
                                            gateway.converge_gateway_id,
                                            pipeline)

    return pipeline.node(gateway.converge_gateway_id)
