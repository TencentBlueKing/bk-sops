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

from pipeline.utils.uniqid import line_uniqid, node_uniqid

from pipeline_web.constants import PWE
from pipeline_web.drawing_new.rank.utils import slack
from pipeline_web.drawing_new.constants import MIN_LEN, DUMMY_NODE_TYPE, DUMMY_FLOW_TYPE
from pipeline_web.drawing_new.utils import delete_flow_id_from_node_io, add_flow_id_to_node_io


def replace_long_path_with_dummy(pipeline, ranks):
    """
    @summary: 使用虚拟节点和虚拟边替换长边
    @param pipeline:
    @param ranks:
    @return: real_flows_chain: 被替换掉的长边
    """
    real_flows_chain = {}
    for flow_id, flow in list(pipeline[PWE.flows].items()):
        flow_slack = slack(ranks, flow)
        if flow_slack > 0:
            real_flows_chain[flow_id] = flow
            dummy_nodes_ranks = range(ranks[flow[PWE.source]] + MIN_LEN, ranks[flow[PWE.target]], MIN_LEN)

            incoming_flow_id = line_uniqid()
            dummy_node_id = node_uniqid()
            dummy_flow = {
                PWE.id: incoming_flow_id,
                PWE.type: DUMMY_FLOW_TYPE,
                PWE.source: flow[PWE.source],
                PWE.target: dummy_node_id
            }
            # change outgoing of flow.source node
            delete_flow_id_from_node_io(pipeline['all_nodes'][flow[PWE.source]], flow_id, PWE.outgoing)
            add_flow_id_to_node_io(pipeline['all_nodes'][flow[PWE.source]], incoming_flow_id, PWE.outgoing)
            # delete long path flow from pipeline
            pipeline[PWE.flows].pop(flow_id)
            for node_rank in dummy_nodes_ranks:
                # 生成当前 dummy node 的 outgoing flow
                outgoing_flow_id = line_uniqid()
                dummy_node = {
                    PWE.id: dummy_node_id,
                    PWE.type: DUMMY_NODE_TYPE,
                    PWE.name: DUMMY_NODE_TYPE,
                    PWE.incoming: incoming_flow_id,
                    PWE.outgoing: outgoing_flow_id
                }

                # add dummy to pipeline
                pipeline['all_nodes'].update({dummy_node_id: dummy_node})
                pipeline[PWE.flows].update({incoming_flow_id: dummy_flow})

                # add dummy to ranks
                ranks.update({dummy_node_id: node_rank})

                # next loop init data
                incoming_flow_id = outgoing_flow_id
                dummy_node_id = node_uniqid()
                dummy_flow = {
                    PWE.id: incoming_flow_id,
                    PWE.type: DUMMY_FLOW_TYPE,
                    PWE.source: dummy_node[PWE.id],
                    PWE.target: dummy_node_id
                }

            # add last dummy flow to pipeline
            dummy_flow[PWE.target] = flow[PWE.target]
            pipeline[PWE.flows].update({incoming_flow_id: dummy_flow})
            # change incoming of flow.target node
            delete_flow_id_from_node_io(pipeline['all_nodes'][flow[PWE.target]], flow_id, PWE.incoming)
            add_flow_id_to_node_io(pipeline['all_nodes'][flow[PWE.target]], incoming_flow_id, PWE.incoming)
    return real_flows_chain


def remove_dummy(pipeline, real_flows_chain, dummy_nodes_included=None, dummy_flows_included=None):
    """
    @summary: 删除虚拟节点
    @param pipeline:
    @param real_flows_chain: 需要被还原的长边
    @param dummy_nodes_included: 需要删除虚拟节点的额外数据，字典格式，删除 key 是虚拟节点ID的项
    @param dummy_flows_included: 需要删除虚拟边的额外数据，字典格式，删除 key 是虚拟边ID的项
    @return:
    """
    # 删除虚拟节点
    if dummy_nodes_included is None:
        dummy_nodes_included = []
    for node_id, node in list(pipeline['all_nodes'].items()):
        if node.get(PWE.type) == DUMMY_NODE_TYPE:
            pipeline['all_nodes'].pop(node_id)
            for dummy_included in dummy_nodes_included:
                if isinstance(dummy_included, dict) and node_id in dummy_included:
                    dummy_included.pop(node_id)

    # 删除虚拟边
    if dummy_flows_included is None:
        dummy_flows_included = []
    for flow_id, flow in list(pipeline[PWE.flows].items()):
        if flow.get(PWE.type) == DUMMY_FLOW_TYPE:
            pipeline[PWE.flows].pop(flow_id)
            for dummy_included in dummy_flows_included:
                if isinstance(dummy_included, dict) and flow_id in dummy_included:
                    dummy_included.pop(flow_id)

            # 虚拟边起始点如果是真实节点，需要把节点引用的虚拟边删除
            if flow[PWE.source] in pipeline['all_nodes']:
                delete_flow_id_from_node_io(pipeline['all_nodes'][flow[PWE.source]], flow_id, PWE.outgoing)
            if flow[PWE.target] in pipeline['all_nodes']:
                delete_flow_id_from_node_io(pipeline['all_nodes'][flow[PWE.target]], flow_id, PWE.incoming)

    # 添加真实长边到节点引用中
    pipeline[PWE.flows].update(real_flows_chain)
    for flow_id, flow in real_flows_chain.items():
        add_flow_id_to_node_io(pipeline['all_nodes'][flow[PWE.source]], flow_id, PWE.outgoing)
        add_flow_id_to_node_io(pipeline['all_nodes'][flow[PWE.target]], flow_id, PWE.incoming)
