# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
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
                PWE.target: dummy_node_id,
            }
            # change outgoing of flow.source node
            delete_flow_id_from_node_io(pipeline["all_nodes"][flow[PWE.source]], flow_id, PWE.outgoing)
            add_flow_id_to_node_io(pipeline["all_nodes"][flow[PWE.source]], incoming_flow_id, PWE.outgoing)
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
                    PWE.outgoing: outgoing_flow_id,
                }

                # add dummy to pipeline
                pipeline["all_nodes"].update({dummy_node_id: dummy_node})
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
                    PWE.target: dummy_node_id,
                }

            # add last dummy flow to pipeline
            dummy_flow[PWE.target] = flow[PWE.target]
            pipeline[PWE.flows].update({incoming_flow_id: dummy_flow})
            # change incoming of flow.target node
            delete_flow_id_from_node_io(pipeline["all_nodes"][flow[PWE.target]], flow_id, PWE.incoming)
            add_flow_id_to_node_io(pipeline["all_nodes"][flow[PWE.target]], incoming_flow_id, PWE.incoming)
    return real_flows_chain


def compute_gateways_detail(pipeline, orders):
    # 每个网关填充的数量为该网关的出口 - 1
    # 搜索网关下所有的网关的个数
    gateways = pipeline["gateways"]
    final_dummy_nums = {}
    # 初始化为每个网关节点进行第一步填充，则网关节点的同一层级需要预留该网关出度的节点的数量 - 1
    for gateway_id, gateway in gateways.items():
        if gateway["type"] in ["ExclusiveGateway", "ParallelGateway"]:
            final_dummy_nums[gateway_id] = len(gateway["outgoing"]) - 1
        if gateway["type"] == "ConvergeGateway":
            final_dummy_nums[gateway_id] = len(gateway["incoming"]) - 1

    # 计算每个网关的前置节点，前置节点的需要预留节点后面的网关的出度的数量 -1 的空间
    nodes_dummy_nums = {}
    for gateway_id, gateway in gateways.items():
        if gateway["type"] in ["ExclusiveGateway", "ParallelGateway"]:
            for incoming in gateway["incoming"]:
                nodes_dummy_nums[pipeline["flows"][incoming]["source"]] = len(gateway["outgoing"]) - 1

    # 根据orders 的顺序得到 节点从后到前到顺序
    nodes_orders_list = []
    gateways_orders_list = []
    for index, nodes in orders.items():
        for node_id in nodes_dummy_nums.keys():
            if node_id in nodes:
                nodes_orders_list.append(node_id)
        for gateway_id in final_dummy_nums.keys():
            if gateway_id in nodes:
                gateways_orders_list.append(gateway_id)

    # 这一部的操作是，如果网关前面是一个节点，网关1 - 节点 - 网关2
    # 那么节点要预留的空间为网关2出度的 - 1
    # 网关1 要预留的空间 = 原本网关要预留的空间+因为嵌套需要额外预留的空间
    for node_id in reversed(nodes_orders_list):
        # node_id 是节点的情况
        if node_id in pipeline["activities"]:
            for incoming in pipeline["activities"][node_id]["incoming"]:
                source_id = pipeline["flows"][incoming]["source"]
                if source_id in final_dummy_nums.keys():
                    final_dummy_nums[source_id] = final_dummy_nums[source_id] + nodes_dummy_nums[node_id]
        else:
            for incoming in gateways[node_id]["incoming"]:
                source_id = pipeline["flows"][incoming]["source"]
                if source_id in final_dummy_nums.keys():
                    final_dummy_nums[source_id] = final_dummy_nums[source_id] + nodes_dummy_nums[node_id]

    # 网关前面到节点需要预留的空间与网关一致
    for gateway_id in reversed(gateways_orders_list):
        if gateways[gateway_id]["type"] in ["ExclusiveGateway", "ParallelGateway"]:
            for incoming in gateways[gateway_id]["incoming"]:
                compute_node_right(pipeline, incoming, final_dummy_nums[gateway_id], nodes_dummy_nums)

    dummy_nums = {}
    # 处理虚拟节点的问题, 左边是网关，需要从左->右 依次修改虚拟节点的填充值
    for node_id, node in pipeline["all_nodes"].items():
        if node["type"] == "DummyNode":
            source_id = pipeline["flows"][node["incoming"]]["source"]
            if source_id in final_dummy_nums.keys():
                dummy_nums[node_id] = final_dummy_nums[source_id]
                # 递归查找该node_id 之后的
                get_dummy_node(pipeline, node["outgoing"], final_dummy_nums[source_id], dummy_nums)

    # 处理虚拟节点的问题，右边是网关，需要从右-左 递归修改虚拟节点的填充值
    final_dummy_nums.update(nodes_dummy_nums)
    final_dummy_nums.update(dummy_nums)
    return final_dummy_nums


def compute_node_right(pipeline, incoming, value, nodes_dummy_nums):
    node_id = pipeline["flows"][incoming]["source"]
    node = pipeline["activities"].get(node_id)
    if node is None:
        return
    nodes_dummy_nums[node_id] = value
    for item in node["incoming"]:
        return compute_node_right(pipeline, item, value, nodes_dummy_nums)

    return


def get_dummy_node(pipeline, outgoing, value, nodes_dummy_nums):
    node_id = pipeline["flows"][outgoing]["target"]
    node = pipeline["all_nodes"].get(node_id)
    if node is None:
        return
    if node["type"] == "DummyNode":
        nodes_dummy_nums[node_id] = value
        return get_dummy_node(pipeline, node["outgoing"], value, nodes_dummy_nums)
    return


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
    for node_id, node in list(pipeline["all_nodes"].items()):
        if node.get(PWE.type) == DUMMY_NODE_TYPE:
            pipeline["all_nodes"].pop(node_id)
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
            if flow[PWE.source] in pipeline["all_nodes"]:
                delete_flow_id_from_node_io(pipeline["all_nodes"][flow[PWE.source]], flow_id, PWE.outgoing)
            if flow[PWE.target] in pipeline["all_nodes"]:
                delete_flow_id_from_node_io(pipeline["all_nodes"][flow[PWE.target]], flow_id, PWE.incoming)

    # 添加真实长边到节点引用中
    pipeline[PWE.flows].update(real_flows_chain)
    for flow_id, flow in real_flows_chain.items():
        add_flow_id_to_node_io(pipeline["all_nodes"][flow[PWE.source]], flow_id, PWE.outgoing)
        add_flow_id_to_node_io(pipeline["all_nodes"][flow[PWE.target]], flow_id, PWE.incoming)
