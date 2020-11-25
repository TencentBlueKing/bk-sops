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

from copy import deepcopy

from pipeline.validators.connection import validate_graph_without_circle

from pipeline_web.constants import PWE
from pipeline_web.drawing_new.utils import (
    add_flow_id_to_node_io,
    delete_flow_id_from_node_io
)


def remove_self_edges(pipeline):
    """
    @summary: 删除自环边
    @return:
    """
    self_edges = {}
    for flow_id, flow in list(pipeline[PWE.flows].items()):
        if flow[PWE.source] == flow[PWE.target]:
            self_edges[flow_id] = flow
            pipeline[PWE.flows].pop(flow_id)
            # delete flow id from node io
            node_id = flow[PWE.source]
            delete_flow_id_from_node_io(pipeline['all_nodes'][node_id], flow_id, PWE.incoming)
            delete_flow_id_from_node_io(pipeline['all_nodes'][node_id], flow_id, PWE.outgoing)
    return self_edges


def insert_self_edges(pipeline, self_edges):
    """
    @summary: 还原自环边
    @return:
    """
    pipeline[PWE.flows].update(self_edges)
    # add flow_id to node io
    for flow_id, flow in self_edges.items():
        node_id = flow[PWE.source]
        add_flow_id_to_node_io(pipeline['all_nodes'][node_id], flow_id, PWE.incoming)
        add_flow_id_to_node_io(pipeline['all_nodes'][node_id], flow_id, PWE.outgoing)


def acyclic_run(pipeline):
    """
    @summary: 逆转反向边
    @return:
    """
    deformed_flows = {'{}.{}'.format(flow[PWE.source], flow[PWE.target]): flow_id
                      for flow_id, flow in pipeline[PWE.flows].items()}
    reversed_flows = {}
    while True:
        no_circle = validate_graph_without_circle(pipeline)
        if no_circle['result']:
            break

        source = no_circle['error_data'][-2]
        target = no_circle['error_data'][-1]
        circle_flow_key = '{}.{}'.format(source, target)
        flow_id = deformed_flows[circle_flow_key]
        reversed_flows[flow_id] = deepcopy(pipeline[PWE.flows][flow_id])
        pipeline[PWE.flows][flow_id].update({
            PWE.source: target,
            PWE.target: source
        })

        source_node = pipeline['all_nodes'][source]
        delete_flow_id_from_node_io(source_node, flow_id, PWE.outgoing)
        add_flow_id_to_node_io(source_node, flow_id, PWE.incoming)

        target_node = pipeline['all_nodes'][target]
        delete_flow_id_from_node_io(target_node, flow_id, PWE.incoming)
        add_flow_id_to_node_io(target_node, flow_id, PWE.outgoing)

    return reversed_flows


def acyclic_undo(pipeline, reversed_flows):
    """
    @summary: 恢复反向边
    @return:
    """
    pipeline[PWE.flows].update(reversed_flows)

    for flow_id, flow in reversed_flows.items():
        source = flow[PWE.source]
        source_node = pipeline['all_nodes'][source]
        delete_flow_id_from_node_io(source_node, flow_id, PWE.incoming)
        add_flow_id_to_node_io(source_node, flow_id, PWE.outgoing)

        target = flow[PWE.target]
        target_node = pipeline['all_nodes'][target]
        delete_flow_id_from_node_io(target_node, flow_id, PWE.outgoing)
        add_flow_id_to_node_io(target_node, flow_id, PWE.incoming)
