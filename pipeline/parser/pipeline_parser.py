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

from copy import deepcopy

from pipeline import exceptions
from pipeline.core.flow import base, activity, gateway, event
from pipeline.core.pipeline import PipelineSpec, Pipeline
from pipeline.core.data.base import DataObject
from pipeline.core.data.context import Context
from pipeline.core.data.converter import get_variable
from pipeline.core.data.hydration import hydrate_subprocess_context, hydrate_node_data
from pipeline.component_framework.library import ComponentLibrary
from pipeline.validators.base import validate_pipeline_tree
from pipeline.core.constants import PE


class PipelineParser(object):

    def __init__(self, pipeline_tree, cycle_tolerate=False):
        validate_pipeline_tree(pipeline_tree, cycle_tolerate=cycle_tolerate)
        self.pipeline_tree = deepcopy(pipeline_tree)

    def parse(self, root_pipeline_data=None, params=None):
        return self._parse(root_pipeline_data, params=params)

    def parser(self, root_pipeline_data=None, params=None):
        return self._parse(root_pipeline_data, params=params)

    def _parse(self, root_pipeline_data=None, params=None, is_subprocess=False, parent_context=None):
        if root_pipeline_data is None:
            root_pipeline_data = {}
        if params is None:
            params = {}
        pipeline_data = deepcopy(root_pipeline_data) if is_subprocess else root_pipeline_data

        pipeline_inputs = self.pipeline_tree[PE.data][PE.inputs]
        act_outputs = {}
        scope_info = {}
        process_params = {}
        for key, info in pipeline_inputs.items():
            if info.get(PE.source_act):
                act_outputs.setdefault(info[PE.source_act],
                                       {}).update({info[PE.source_key]: key})
                continue

            is_param = info.get(PE.is_param, False)
            info = params.get(key, info) if is_param else info

            if is_subprocess and is_param:
                process_params.update({key: info})
                continue

            scope_info.update({key: info})

        output_keys = self.pipeline_tree[PE.data][PE.outputs]
        context = Context(act_outputs, output_keys)
        for key, info in scope_info.items():
            var = get_variable(key, info, context, pipeline_data)
            context.set_global_var(key, var)

        if is_subprocess:
            if parent_context is None:
                raise exceptions.DataTypeErrorException('parent context of subprocess cannot be none')
            for key, info in process_params.items():
                var = get_variable(key, info, parent_context, pipeline_data)
                pipeline_data.update({key: var})

        start = self.pipeline_tree[PE.start_event]
        start_cls = getattr(event, start[PE.type])
        start_event = start_cls(id=start[PE.id],
                                name=start[PE.name])

        end = self.pipeline_tree[PE.end_event]
        end_cls = getattr(event, end[PE.type])
        end_event = end_cls(id=end[PE.id],
                            name=end[PE.name])

        acts = self.pipeline_tree[PE.activities]
        act_objs = []
        for act in acts.values():
            act_cls = getattr(activity, act[PE.type])
            if act[PE.type] == PE.ServiceActivity:
                component = ComponentLibrary.get_component(
                    act[PE.component][PE.code], act[PE.component][PE.inputs]
                )
                service = component.service()
                data = component.data_for_execution(context, pipeline_data)
                act_objs.append(act_cls(id=act[PE.id],
                                        service=service,
                                        name=act[PE.name],
                                        data=data,
                                        error_ignorable=act.get(PE.error_ignorable, False),
                                        skippable=act.get(PE.skippable, True),
                                        can_retry=act.get(PE.can_retry, True),
                                        timeout=act.get(PE.timeout)))
            elif act[PE.type] == PE.SubProcess:
                sub_tree = act[PE.pipeline]
                params = act[PE.params]
                sub_parser = PipelineParser(pipeline_tree=sub_tree)
                act_objs.append(act_cls(id=act[PE.id],
                                        pipeline=sub_parser._parse(
                                            root_pipeline_data=root_pipeline_data,
                                            params=params,
                                            is_subprocess=True,
                                            parent_context=context),
                                        name=act[PE.name]))
            else:
                raise exceptions.FlowTypeError(u"Unknown Activity type: %s" %
                                               act[PE.type])

        gateways = self.pipeline_tree[PE.gateways]
        flows = self.pipeline_tree[PE.flows]
        gateway_objs = []
        for gw in gateways.values():
            gw_cls = getattr(gateway, gw[PE.type])
            if gw[PE.type] in {PE.ParallelGateway, PE.ConditionalParallelGateway}:
                gateway_objs.append(
                    gw_cls(id=gw[PE.id],
                           converge_gateway_id=gw[PE.converge_gateway_id],
                           name=gw[PE.name]))
            elif gw[PE.type] in {PE.ExclusiveGateway, PE.ConvergeGateway}:
                gateway_objs.append(gw_cls(id=gw[PE.id],
                                           name=gw[PE.name]))
            else:
                raise exceptions.FlowTypeError(u"Unknown Gateway type: %s" %
                                               gw[PE.type])

        flow_objs_dict = {}
        for fl in flows.values():
            flow_nodes = act_objs + gateway_objs
            if fl[PE.source] == start[PE.id]:
                source = start_event
            else:
                source = filter(lambda x: x.id == fl[PE.source], flow_nodes)[0]
            if fl[PE.target] == end[PE.id]:
                target = end_event
            else:
                target = filter(lambda x: x.id == fl[PE.target], flow_nodes)[0]
            flow_objs_dict[fl[PE.id]] = base.SequenceFlow(fl[PE.id],
                                                          source,
                                                          target)
        flow_objs = flow_objs_dict.values()

        # add incoming and outgoing flow to acts
        if not isinstance(start[PE.outgoing], list):
            start[PE.outgoing] = [start[PE.outgoing]]
        for outgoing_id in start[PE.outgoing]:
            start_event.outgoing.add_flow(flow_objs_dict[outgoing_id])

        if not isinstance(end[PE.incoming], list):
            end[PE.incoming] = [end[PE.incoming]]
        for incoming_id in end[PE.incoming]:
            end_event.incoming.add_flow(flow_objs_dict[incoming_id])

        for act in act_objs:
            incoming = acts[act.id][PE.incoming]
            if isinstance(incoming, list):
                for s in incoming:
                    act.incoming.add_flow(flow_objs_dict[s])
            else:
                act.incoming.add_flow(flow_objs_dict[incoming])

            act.outgoing.add_flow(flow_objs_dict[acts[act.id][PE.outgoing]])

        for gw in gateway_objs:
            if isinstance(gw, gateway.ExclusiveGateway) or isinstance(gw, gateway.ConditionalParallelGateway):
                for flow_id, con in gateways[gw.id][PE.conditions].items():
                    con_obj = gateway.Condition(
                        con[PE.evaluate],
                        flow_objs_dict[flow_id],
                    )
                    gw.add_condition(con_obj)

                if isinstance(gateways[gw.id][PE.incoming], list):
                    for incoming_id in gateways[gw.id][PE.incoming]:
                        gw.incoming.add_flow(flow_objs_dict[incoming_id])
                else:
                    gw.incoming.add_flow(
                        flow_objs_dict[gateways[gw.id][PE.incoming]]
                    )

                for outgoing_id in gateways[gw.id][PE.outgoing]:
                    gw.outgoing.add_flow(flow_objs_dict[outgoing_id])

            elif isinstance(gw, gateway.ParallelGateway):
                if isinstance(gateways[gw.id][PE.incoming], list):
                    for incoming_id in gateways[gw.id][PE.incoming]:
                        gw.incoming.add_flow(flow_objs_dict[incoming_id])
                else:
                    gw.incoming.add_flow(
                        flow_objs_dict[gateways[gw.id][PE.incoming]]
                    )

                for outgoing_id in gateways[gw.id][PE.outgoing]:
                    gw.outgoing.add_flow(flow_objs_dict[outgoing_id])

            elif isinstance(gw, gateway.ConvergeGateway):
                for incoming_id in gateways[gw.id][PE.incoming]:
                    gw.incoming.add_flow(flow_objs_dict[incoming_id])
                gw.outgoing.add_flow(
                    flow_objs_dict[gateways[gw.id][PE.outgoing]]
                )

            else:
                raise exceptions.FlowTypeError(u"Unknown Gateway type: %s" %
                                               type(gw))

        context.duplicate_variables()
        pipeline_data = DataObject(pipeline_data)
        pipeline_spec = PipelineSpec(start_event, end_event, flow_objs,
                                     act_objs, gateway_objs, pipeline_data,
                                     context)
        return Pipeline(self.pipeline_tree[PE.id], pipeline_spec)

    def get_act(self, act_id, subprocess_stack=None, root_pipeline_data=None):
        if subprocess_stack is None:
            subprocess_stack = []
        if root_pipeline_data is None:
            root_pipeline_data = {}

        subprocess = self.parse(root_pipeline_data)
        for sub_id in subprocess_stack:
            subprocess_act = filter(lambda x: x.id == sub_id,
                                    subprocess.spec.activities)[0]
            hydrate_subprocess_context(subprocess_act)
            subprocess = subprocess_act.pipeline
        act = filter(lambda x: x.id == act_id, subprocess.spec.activities)[0]
        return act

    def get_act_inputs(self, act_id, subprocess_stack=None, root_pipeline_data=None):
        act = self.get_act(act_id, subprocess_stack, root_pipeline_data)
        hydrate_node_data(act)
        inputs = act.data.inputs
        return inputs
