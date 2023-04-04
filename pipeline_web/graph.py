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
