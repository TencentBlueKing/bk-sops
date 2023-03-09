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


def compute_sorted_list_by_order(orders, dummy_nums_dict):
    # 根据orders 的顺序得到, 得到节点和网关的排序
    result = []
    for index, nodes in orders.items():
        for node_id in dummy_nums_dict.keys():
            if node_id in nodes:
                result.append(node_id)
    return result


def compute_node_right_to_left(pipeline, incoming, value, nodes_dummy_nums):
    # 从右到左向前搜索
    node_id = pipeline[PWE.flows][incoming][PWE.source]
    node = pipeline[PWE.activities].get(node_id)
    if node is None:
        return
    nodes_dummy_nums[node_id] = value
    for item in node[PWE.incoming]:
        return compute_node_right_to_left(pipeline, item, value, nodes_dummy_nums)

    return


def compute_node_left_to_right(pipeline, outgoing, value, nodes_dummy_nums):
    # 从左到右向后搜索，处理虚拟节点
    node_id = pipeline[PWE.flows][outgoing][PWE.target]
    node = pipeline["all_nodes"].get(node_id)
    if node is None:
        return
    # 如果发现是虚拟节点，继续向下递归
    if node["type"] == "DummyNode":
        nodes_dummy_nums[node_id] = value
        return compute_node_left_to_right(pipeline, node["outgoing"], value, nodes_dummy_nums)
    return


def compute_nodes_fill_num(pipeline, orders):
    # 先拿到所有的网关
    gateways = pipeline["gateways"]
    # 最终排序的结果
    final_dummy_nums = {}

    # 初始化为每个网关节点进行第一步填充，则网关节点的同一层级需要预留该网关出度的节点的数量 - 1
    for gateway_id, gateway in gateways.items():
        # 分支网关，并行网关，条件并行网关 默认填充网关出口的数量 - 1
        if gateway["type"] in [PWE.ExclusiveGateway, PWE.ParallelGateway, PWE.ConditionalParallelGateway]:
            final_dummy_nums[gateway_id] = len(gateway[PWE.outgoing]) - 1
        # 汇聚网关填充网关入口的数量 - 1
        if gateway["type"] == PWE.ConvergeGateway:
            final_dummy_nums[gateway_id] = len(gateway[PWE.incoming]) - 1

    # TODO 可能有最优的解，从后向前计算只排一次
    # 把网关的前置节点都挑选出来
    # 计算每个网关的前置节点，前置节点的需要预留节点后面的网关的出度的数量 -1 的空间
    # 节点 - 网关， 那么节点会继承后面网关的占用数量，如果节点后面的网关有三条分支，那么节点的下方需要预留出两条分支的位置给后方的网关
    nodes_dummy_nums = {}
    for gateway_id, gateway in gateways.items():
        if gateway["type"] in [PWE.ExclusiveGateway, PWE.ParallelGateway, PWE.ConditionalParallelGateway]:
            for incoming in gateway[PWE.incoming]:
                value = len(gateway[PWE.outgoing]) - 1
                nodes_dummy_nums[pipeline[PWE.flows][incoming][PWE.source]] = value
                # 需要第一波计算, 将节点的空间值传递到前面的节点
                # 网关=节点1=节点2-节点网关
                # 节点1的值=节点2的值
                compute_node_right_to_left(pipeline, incoming, value, nodes_dummy_nums)

    nodes_orders_list = compute_sorted_list_by_order(orders, nodes_dummy_nums)

    # 如果节点的前面是一个网关，那么网关需要预留的空间=网关需要预留的空间+节点需要预留的空间
    for node_id in reversed(nodes_orders_list):
        # node_id 是节点的情况
        if node_id in pipeline[PWE.activities].keys():
            # 节点只存在一个incoming，所以只需要处理一次
            for incoming in pipeline[PWE.activities][node_id][PWE.incoming]:
                source_id = pipeline[PWE.flows][incoming][PWE.source]
                if source_id in final_dummy_nums.keys():
                    value = final_dummy_nums[source_id] + nodes_dummy_nums[node_id]
                    final_dummy_nums[source_id] = value
                    # 网关前面的的节点需要重新计算
                    gateway = gateways[source_id]
                    # 针对汇聚网关之前的节点，暂时取消向前更新赋值
                    if gateway["type"] in [PWE.ExclusiveGateway, PWE.ParallelGateway, PWE.ConditionalParallelGateway]:
                        for gateway_incoming in gateway[PWE.incoming]:
                            compute_node_right_to_left(pipeline, gateway_incoming, value, nodes_dummy_nums)

    converge_gateway_node_nums = {}
    # 所有分支网关，条件分支网关，条件网关的汇聚网关与之一致
    for gateway_id, value in final_dummy_nums.items():
        gateway = gateways[gateway_id]
        if gateway["type"] in [PWE.ExclusiveGateway, PWE.ParallelGateway, PWE.ConditionalParallelGateway]:
            # 找到对应的汇聚网关
            if "converge_gateway_id" in gateway:
                converge_gateway_id = gateway["converge_gateway_id"]
                converge_gateway_node_nums[converge_gateway_id] = value

    final_dummy_nums.update(converge_gateway_node_nums)
    final_dummy_nums.update(nodes_dummy_nums)

    # 汇聚网关向后搜索，如果是虚拟节点，则值和网关一致
    dummy_node_nums = {}
    # 处理虚拟节点的问题, 左边是汇聚网关的情况，需要从左->右 依次修改虚拟节点的填充值
    for node_id, node in pipeline["all_nodes"].items():
        if node["type"] == "DummyNode":
            source_id = pipeline[PWE.flows][node[PWE.incoming]][PWE.source]
            if source_id in final_dummy_nums.keys():
                dummy_node_nums[node_id] = final_dummy_nums[source_id]
                # 递归查找该node_id 之后的
                compute_node_left_to_right(pipeline, node[PWE.outgoing], final_dummy_nums[source_id], dummy_node_nums)

    final_dummy_nums.update(dummy_node_nums)
    return final_dummy_nums


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
