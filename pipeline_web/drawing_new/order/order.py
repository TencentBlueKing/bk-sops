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

from pipeline.core.constants import PE
from pipeline.validators.utils import format_to_list

from pipeline_web.drawing_new.constants import MIN_LEN
from pipeline_web.drawing_new.rank.utils import max_rank, min_rank

# 启发式层级内顶点排序最大迭代次数，参考《A Technique for Drawing Directed Graphs》设置
MAX_ORDERING_LOOP = 24


def ordering(pipeline, ranks):
    """
    @summary:
    @param pipeline:
    @param ranks:
    @return:
    """
    orders = init_order(pipeline, ranks)
    best = deepcopy(orders)
    best_count = crossing_count(pipeline, best)
    for loop in range(MAX_ORDERING_LOOP):
        wmedian(pipeline, orders, loop, ranks)
        if crossing_count(pipeline, orders) < best_count:
            best = orders
        elif loop % 2 == 0:
            break
    return best


def init_order(pipeline, ranks):
    """
    @summary: 根据 ranks 快速生成初始化的层级内顶点排序 orders
    @param pipeline:
    @param ranks:
    @return:
    """
    orders = {rk: [] for rk in set(ranks.values())}
    rk = min_rank(ranks)
    orders[rk] = [node_id for node_id, node_rk in ranks.items() if node_rk == rk]

    while rk < max_rank(ranks):
        next_layer_rk = rk + MIN_LEN
        for node_id in orders[rk]:
            node = pipeline['all_nodes'][node_id]
            for flow_id in format_to_list(node[PE.outgoing]):
                flow = pipeline[PE.flows][flow_id]
                if flow[PE.target] not in orders[next_layer_rk]:
                    orders[next_layer_rk].append(flow[PE.target])
        rk = next_layer_rk

    return orders


def wmedian(pipeline, orders, loop, ranks):
    """
    @summary: 启发式加权中位数算法计算相邻层级内顶点权重
    @param pipeline:
    @param orders:
    @param loop:
    @param ranks:
    @return:
    """
    min_rk = min_rank(ranks)
    max_rk = max_rank(ranks)
    if loop % 2 == 0:
        for r in range(min_rk + MIN_LEN, max_rk + MIN_LEN, MIN_LEN):
            median_r = []
            for node_id in orders[r]:
                refer_nodes = refer_node_ids(pipeline, node_id, PE.incoming)
                median_r.append(median_value(refer_nodes, orders[r - MIN_LEN]))
            orders[r] = sort_layer(orders[r], median_r)
    else:
        for r in range(max_rk - MIN_LEN, min_rk - MIN_LEN, - MIN_LEN):
            median_r = []
            for node_id in orders[r]:
                refer_nodes = refer_node_ids(pipeline, node_id, PE.outgoing)
                median_r.append(median_value(refer_nodes, orders[r + MIN_LEN]))
            orders[r] = sort_layer(orders[r], median_r)


def refer_node_ids(pipeline, node_id, io):
    node = pipeline['all_nodes'][node_id]
    refer_nodes = []
    flow_direction = PE.source if io == PE.incoming else PE.target
    for flow_id in format_to_list(node[io]):
        refer_nodes.append(pipeline[PE.flows][flow_id][flow_direction])
    return refer_nodes


def median_value(refer_nodes, refer_layer_orders):
    """
    @summary: 根据相邻层有连接的点求中位数
    @param refer_nodes:
    @param refer_layer_orders:
    @return:
    """
    layer_orders_index = sorted([refer_layer_orders.index(ref) for ref in refer_nodes])
    refer_len = len(layer_orders_index)
    # 没有相邻顶点的节点中位数值被设置为-1，让这些节点维持原来位置
    if refer_len == 0:
        return -1
    elif refer_len % 2 == 1:
        return layer_orders_index[refer_len // 2]
    else:
        return (layer_orders_index[(refer_len // 2) - 1] + layer_orders_index[refer_len // 2]) / 2


def sort_layer(layer_order, weight):
    """
    @summary: 根据权重排序，注意权重为 -1 的位置不能变更
        e.g.1: layer_order -> ['a', 'b', 'c', 'd', 'e', 'f']
               weight -> [3, -1, 2, -1, 5, 4]
               return -> ['c', 'b', 'a', 'd', 'f', 'e']
    @param layer_order:
    @param weight:
    @return:
    """
    to_sort = []
    persist = []
    for index, item in enumerate(layer_order):
        if weight[index] == -1:
            persist.append((item, index))
        else:
            to_sort.append((item, weight[index]))
    to_sort.sort(key=lambda x: x[1])
    layer_order_sorted = [item[0] for item in to_sort]
    for item in persist:
        layer_order_sorted.insert(item[1], item[0])
    return layer_order_sorted


def crossing_count(pipeline, orders):
    count = 0
    for rk in range(min(list(orders.keys())), max(list(orders.keys())), MIN_LEN):
        current_layer_nodes = orders[rk]
        next_layer_nodes = orders[rk + MIN_LEN]
        current_layer_flows = [flow for flow in pipeline[PE.flows].values()
                               if flow[PE.source] in current_layer_nodes and flow[PE.target] in next_layer_nodes]
        if len(current_layer_flows) >= 2:
            for flow_index in range(len(current_layer_flows) - 1):
                first_flow = current_layer_flows[flow_index]
                first_source_index = current_layer_nodes.index(first_flow[PE.source])
                first_target_index = next_layer_nodes.index(first_flow[PE.target])

                for next_flow_index in range(flow_index + 1, len(current_layer_flows)):
                    next_flow = current_layer_flows[next_flow_index]
                    next_source_index = current_layer_nodes.index(next_flow[PE.source])
                    next_target_index = next_layer_nodes.index(next_flow[PE.target])
                    # 起始点次序不一致说明有交叉
                    if (first_source_index - next_source_index) * (first_target_index - next_target_index) < 0:
                        count += 1
    return count
