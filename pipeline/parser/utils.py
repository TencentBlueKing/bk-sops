# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
import logging

from pipeline.utils.uniqid import uniqid, node_uniqid, line_uniqid
from pipeline.core.constants import PE
from pipeline.exceptions import NodeNotExistException

logger = logging.getLogger('root')

ID = 'id'
CVG_GW_ID = 'converge_gateway_id'


def replace_all_id(pipeline_data):
    flows = pipeline_data['flows']
    node_map = {}
    flow_map = {}

    # step.1 replace nodes id

    # replace events id
    start_event_id = node_uniqid()
    end_event_id = node_uniqid()
    node_map[pipeline_data[PE.start_event][ID]] = start_event_id
    node_map[pipeline_data[PE.end_event][ID]] = end_event_id

    _replace_event_id(flows, pipeline_data[PE.start_event], start_event_id)
    _replace_event_id(flows, pipeline_data[PE.end_event], end_event_id)

    # replace activities id
    activities = pipeline_data[PE.activities]
    keys = activities.keys()
    for old_id in keys:
        substituted_id = node_uniqid()
        node_map[old_id] = substituted_id
        _replace_activity_id(flows, activities, old_id, substituted_id)

    # replace gateways id
    gateways = pipeline_data[PE.gateways]
    keys = gateways.keys()
    for old_id in keys:
        substituted_id = node_uniqid()
        node_map[old_id] = substituted_id
        _replace_gateway_id(flows, gateways, old_id, substituted_id)

    # step.2 replace flows id
    keys = flows.keys()
    for old_id in keys:
        substituted_id = line_uniqid()
        flow_map[old_id] = substituted_id
        _replace_flow_id(flows, old_id, substituted_id, pipeline_data)

    # step.3 replace front end data
    _replace_front_end_data_id(pipeline_data, node_map, flow_map)


def _replace_front_end_data_id(pipeline_data, node_map, flow_map):
    if PE.line in pipeline_data:
        for line in pipeline_data[PE.line]:
            line['id'] = flow_map[line['id']]
            line['source']['id'] = node_map[line['source']['id']]
            line['target']['id'] = node_map[line['target']['id']]
    if PE.location in pipeline_data:
        for location in pipeline_data[PE.location]:
            location['id'] = node_map[location['id']]
    if PE.constants in pipeline_data:
        for key, constant in pipeline_data[PE.constants].iteritems():
            source_info = constant.get('source_info', None)
            if source_info:
                replaced_constant = {}
                for source_step, source_keys in source_info.iteritems():
                    try:
                        replaced_constant[node_map[source_step]] = source_keys
                    except KeyError as e:
                        message = 'replace pipeline template id error: %s' % e
                        logger.exception(message)
                        raise NodeNotExistException(message)
                    constant['source_info'] = replaced_constant


def _replace_flow_id(flows, flow_id, substituted_id, pipeline_data):
    flow = flows[flow_id]
    flow[ID] = substituted_id

    _replace_flow_in_node(flow[PE.source], pipeline_data, substituted_id, flow_id, PE.outgoing)
    _replace_flow_in_node(flow[PE.target], pipeline_data, substituted_id, flow_id, PE.incoming)

    flows.pop(flow_id)
    flows[substituted_id] = flow


def _replace_flow_in_node(node_id, pipeline_data, substituted_id, flow_id, field):
    if node_id in pipeline_data[PE.activities]:
        pipeline_data[PE.activities][node_id][field] = substituted_id
    elif node_id in pipeline_data[PE.gateways]:
        gateway = pipeline_data[PE.gateways][node_id]
        _replace_flow_in_gateway(gateway, substituted_id, flow_id, field)
    elif node_id == pipeline_data[PE.start_event][ID]:
        pipeline_data[PE.start_event][PE.outgoing] = substituted_id
    elif node_id == pipeline_data[PE.end_event][ID]:
        pipeline_data[PE.end_event][PE.incoming] = substituted_id


def _replace_flow_in_gateway(gateway, substituted_id, flow_id, field):
    if isinstance(gateway[field], list):
        gateway[field].remove(flow_id)
        gateway[field].append(substituted_id)

        if gateway['type'] == 'ExclusiveGateway':
            conditions = gateway['conditions']
            conditions[substituted_id] = conditions[flow_id]
            conditions.pop(flow_id)
    else:
        gateway[field] = substituted_id


def _replace_gateway_id(flows, gateways, gateway_id, substituted_id):
    try:
        gateway = gateways[gateway_id]
        gateway[ID] = substituted_id

        if gateway['type'] == 'ConvergeGateway':
            flows[gateway[PE.outgoing]][PE.source] = substituted_id
            for flow_id in gateway[PE.incoming]:
                flows[flow_id][PE.target] = substituted_id
            # replace converge_gateway_id
            for g_id, gw in gateways.iteritems():
                if CVG_GW_ID in gw and gw[CVG_GW_ID] == gateway_id:
                    gw[CVG_GW_ID] = substituted_id
        else:
            flows[gateway[PE.incoming]][PE.target] = substituted_id
            for flow_id in gateway[PE.outgoing]:
                flows[flow_id][PE.source] = substituted_id

        gateways.pop(gateway_id)
        gateways[substituted_id] = gateway
    except KeyError as e:
        message = 'replace gateway id error: %s' % e
        logger.exception(message)
        raise NodeNotExistException(message)


def _replace_activity_id(flows, activities, act_id, substituted_id):
    try:
        activity = activities[act_id]
        activity[ID] = substituted_id

        flows[activity[PE.incoming]][PE.target] = substituted_id
        flows[activity[PE.outgoing]][PE.source] = substituted_id

        activities.pop(act_id)
        activities[substituted_id] = activity
    except KeyError as e:
        message = 'replace activity id error: %s' % e
        logger.exception(message)
        raise NodeNotExistException(message)


def _replace_event_id(flows, event, substituted_id):
    try:
        event[ID] = substituted_id
        if event[PE.incoming]:
            flows[event[PE.incoming]][PE.target] = substituted_id
        else:
            flows[event[PE.outgoing]][PE.source] = substituted_id
    except KeyError as e:
        message = 'replace event id error: %s' % e
        logger.exception(message)
        raise NodeNotExistException(message)
