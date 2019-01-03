# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
from pipeline.parser.format import format_web_data_to_pipeline
from pipeline import exceptions
from pipeline.core.flow import base, activity, gateway, event
from pipeline.core.pipeline import PipelineSpec, Pipeline
from pipeline.core.data.base import DataObject
from pipeline.core.data.context import Context
from pipeline.core.data.converter import get_variable
from pipeline.component_framework.library import ComponentLibrary
from pipeline.validators.base import (
    validate_web_pipeline_tree,
    validate_pipeline_tree,
)


class PipelineParser(object):

    def __init__(self, pipeline_tree):

        validate_pipeline_tree(pipeline_tree)
        self.pipeline_tree = pipeline_tree

    def parser(self, root_pipeline_data=None):
        if root_pipeline_data is None:
            root_pipeline_data = {}

        pipeline_inputs = self.pipeline_tree['data']['inputs']
        act_outputs = {}
        scope_info = {}
        for key, info in pipeline_inputs.iteritems():
            if info.get('source_act'):
                act_outputs.setdefault(info['source_act'],
                                       {}).update({info['source_key']: key})
            else:
                scope_info.update({key: info})
        output_keys = self.pipeline_tree['data']['outputs'].keys()
        context = Context(act_outputs, output_keys)
        for key, info in scope_info.iteritems():
            value = get_variable(key, info, context, root_pipeline_data)
            context.set_global_var(key, value)

        start = self.pipeline_tree['start_event']
        start_cls = getattr(event, start['type'])
        start_event = start_cls(id=start['id'],
                                name=start['name'])

        end = self.pipeline_tree['end_event']
        end_cls = getattr(event, end['type'])
        end_event = end_cls(id=end['id'],
                            name=end['name'])

        acts = self.pipeline_tree['activities']
        act_objs = []
        for act in acts.values():
            act_cls = getattr(activity, act['type'])
            if act['type'] == 'ServiceActivity':
                component = ComponentLibrary.get_component(
                    act['component']['code'], act['component']['inputs']
                )
                service = component.service()
                data = component.data_for_execution(context, root_pipeline_data)
                act_objs.append(act_cls(id=act['id'],
                                        service=service,
                                        name=act['name'],
                                        data=data,
                                        error_ignorable=act.get('error_ignorable', False)))
            elif act['type'] == 'SubProcess':
                pipeline_info = act['pipeline']
                sub_parser = PipelineParser(pipeline_info)
                act_objs.append(act_cls(id=act['id'],
                                        pipeline=sub_parser.parser(root_pipeline_data),
                                        name=act['name']))
            else:
                raise exceptions.FlowTypeError(u"Unknown Activity type: %s" %
                                               act['type'])

        gateways = self.pipeline_tree['gateways']
        flows = self.pipeline_tree['flows']
        gateway_objs = []
        for gw in gateways.values():
            gw_cls = getattr(gateway, gw['type'])
            if gw['type'] in ['ParallelGateway']:
                gateway_objs.append(
                    gw_cls(id=gw['id'],
                           converge_gateway_id=gw['converge_gateway_id'],
                           name=gw['name']))
            elif gw['type'] in ['ExclusiveGateway', 'ConvergeGateway']:
                gateway_objs.append(gw_cls(id=gw['id'],
                                           name=gw['name']))
            else:
                raise exceptions.FlowTypeError(u"Unknown Gateway type: %s" %
                                               gw['type'])

        flow_objs_dict = {}
        for fl in flows.values():
            flow_nodes = act_objs + gateway_objs
            if fl['source'] == start['id']:
                source = start_event
            else:
                source = filter(lambda x: x.id == fl['source'], flow_nodes)[0]
            if fl['target'] == end['id']:
                target = end_event
            else:
                target = filter(lambda x: x.id == fl['target'], flow_nodes)[0]
            flow_objs_dict[fl['id']] = base.SequenceFlow(fl['id'],
                                                         source,
                                                         target)
        flow_objs = flow_objs_dict.values()

        # add incoming and outgoing flow to acts
        if not isinstance(start['outgoing'], list):
            start['outgoing'] = [start['outgoing']]
        for outgoing_id in start['outgoing']:
            start_event.outgoing.add_flow(flow_objs_dict[outgoing_id])

        if not isinstance(end['incoming'], list):
            end['incoming'] = [end['incoming']]
        for incoming_id in end['incoming']:
            end_event.incoming.add_flow(flow_objs_dict[incoming_id])

        for act in act_objs:
            act.incoming.add_flow(flow_objs_dict[acts[act.id]['incoming']])
            act.outgoing.add_flow(flow_objs_dict[acts[act.id]['outgoing']])

        for gw in gateway_objs:
            if isinstance(gw, gateway.ExclusiveGateway):
                for flow_id, con in gateways[gw.id]['conditions'].iteritems():
                    con_obj = gateway.Condition(
                        con['evaluate'],
                        flow_objs_dict[flow_id],
                    )
                    gw.add_condition(con_obj)
                gw.incoming.add_flow(
                    flow_objs_dict[gateways[gw.id]['incoming']]
                )
                for outgoing_id in gateways[gw.id]['outgoing']:
                    gw.outgoing.add_flow(flow_objs_dict[outgoing_id])

            elif isinstance(gw, gateway.ParallelGateway):
                gw.incoming.add_flow(
                    flow_objs_dict[gateways[gw.id]['incoming']]
                )
                for outgoing_id in gateways[gw.id]['outgoing']:
                    gw.outgoing.add_flow(flow_objs_dict[outgoing_id])

            elif isinstance(gw, gateway.ConvergeGateway):
                for incoming_id in gateways[gw.id]['incoming']:
                    gw.incoming.add_flow(flow_objs_dict[incoming_id])
                gw.outgoing.add_flow(
                    flow_objs_dict[gateways[gw.id]['outgoing']]
                )

            else:
                raise exceptions.FlowTypeError(u"Unknown Gateway type: %s" %
                                               type(gw))

        root_pipeline_data = DataObject(root_pipeline_data)
        pipeline_spec = PipelineSpec(start_event, end_event, flow_objs,
                                     act_objs, gateway_objs, root_pipeline_data,
                                     context)
        return Pipeline(self.pipeline_tree['id'], pipeline_spec)

    def get_act(self, act_id, subprocess_stack=None, root_pipeline_data=None):
        if subprocess_stack is None:
            subprocess_stack = []
        if root_pipeline_data is None:
            root_pipeline_data = {}

        subprocess = self.parser(root_pipeline_data).spec
        for sub_id in subprocess_stack:
            subprocess = filter(lambda x: x.id == sub_id,
                                subprocess.activities)[0].pipeline.spec
        act = filter(lambda x: x.id == act_id, subprocess.activities)[0]
        return act

    def get_act_inputs(self, act_id, subprocess_stack=None, root_pipeline_data=None):
        act = self.get_act(act_id, subprocess_stack, root_pipeline_data)
        inputs = {key: info.get()
                  for key, info in act.data.inputs.iteritems()}
        return inputs


class WebPipelineAdapter(PipelineParser):

    def __init__(self, web_pipeline_tree):

        validate_web_pipeline_tree(web_pipeline_tree)
        pipeline_tree = format_web_data_to_pipeline(web_pipeline_tree)
        super(WebPipelineAdapter, self).__init__(pipeline_tree)
