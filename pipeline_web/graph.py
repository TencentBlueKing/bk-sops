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

import networkx as nx
from pipeline.core.constants import PE


def get_graph_from_pipeline_tree(pipeline_tree):
    nodes = (
        [pipeline_tree[PE.end_event]["id"], pipeline_tree[PE.start_event]["id"]]
        + list(pipeline_tree[PE.activities].keys())
        + list(pipeline_tree[PE.gateways].keys())
    )
    edges = [(flow["source"], flow["target"], {"id": flow_id}) for flow_id, flow in pipeline_tree[PE.flows].items()]
    graph = nx.DiGraph()
    graph.add_nodes_from([(node, {"labels": set()}) for node in nodes])
    graph.add_edges_from(edges)
    return graph


def get_necessary_nodes_and_paths_between_nodes(nx_graph, start, end):
    """获取两个节点之间的必要节点"""
    paths = list(nx.all_simple_paths(nx_graph, start, end))
    necessary_nodes = set(nx_graph.nodes)
    for path in paths:
        necessary_nodes &= set(path)
    return necessary_nodes, paths


def get_ordered_necessary_nodes_and_paths_between_nodes(nx_graph, start, end):
    """获取两个节点之间的必要节点"""
    unordered_nodes, paths = get_necessary_nodes_and_paths_between_nodes(nx_graph, start, end)
    ordered_nodes = []
    if paths:
        [ordered_nodes.append(node) for node in paths[0] if node in unordered_nodes]
    return ordered_nodes, paths


def get_all_nodes_and_edge_between_nodes(nx_graph, start, end):
    """获取两个节点之间的所有节点和边"""
    nodes, edges = set(), set()
    node_paths = nx.all_simple_paths(nx_graph, start, end)
    for node_path in node_paths:
        nodes |= set(node_path)

    edge_paths = nx.all_simple_edge_paths(nx_graph, start, end)
    for edge_path in edge_paths:
        edge_ids = set([nx_graph.edges[edge]["id"] for edge in edge_path])
        edges |= edge_ids

    return nodes, edges


def check_node_in_circle(nx_graph, node):
    """检查节点是否在环中"""
    try:
        circle = nx.find_cycle(nx_graph, node)
    except nx.NetworkXNoCycle:
        return False
    return True if circle else False


def get_all_nodes_and_edges_in_circle(nx_graph, node):
    """获取环中的所有节点和边"""
    nodes, edges = set(), set()
    circles = nx.simple_cycles(nx_graph)
    for circle in circles:
        if node in circle:
            nodes |= set(circle)
            for line_path in zip(circle, circle[1:] + circle[:1]):
                edges.add(nx_graph.edges[line_path]["id"])
    return nodes, edges
