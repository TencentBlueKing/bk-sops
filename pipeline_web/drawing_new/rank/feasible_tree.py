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

from pipeline.core.constants import PE
from pipeline.validators.utils import format_to_list

from pipeline_web.drawing_new.rank.utils import slack


def feasible_tree_ranker(pipeline, ranks):
    """
    @summary: 最优可行树分配层级
    @param pipeline:
    @param ranks:
    @return:
    @example:
                +---+        +---+        +---+
               >| B |------->| C |------->| E |
             -/ +---+        +---+        +---+
           -/     -1           0            1
    +---+-/     +---+        +---+
    | A |------>| D |------->| F |
    +---+-\     +---+        +---+
     -2    -\     -1           0
             -\ +---+        +---+        +---+        +---+
               >| G |------->| H |------->| I |------->| J |
                +---+        +---+        +---+        +---+
                  -1           0            1            2
    """  # noqa
    part_tree = {
        'all_nodes': {
            pipeline[PE.start_event][PE.id]: pipeline[PE.start_event]
        },
        PE.flows: {}
    }

    node_count = len(list(pipeline['all_nodes'].keys()))
    while tight_tree(part_tree, pipeline, ranks) < node_count:
        flow = find_min_slack_flow(part_tree, pipeline, ranks)
        delta = slack(ranks, flow)
        if flow[PE.target] in part_tree['all_nodes']:
            delta = -delta
        shift_ranks(ranks, list(part_tree['all_nodes'].keys()), delta)

    return ranks


def tight_tree(part_tree, pipeline, ranks):

    def dfs(node):
        for direction in [PE.outgoing, PE.incoming]:
            for flow_id in format_to_list(node[direction]):
                flow = pipeline[PE.flows][flow_id]
                direct_key = PE.target if direction == PE.outgoing else PE.source
                direct_node_id = flow[direct_key]
                direct_node = pipeline['all_nodes'][direct_node_id]
                if direct_node_id not in part_tree['all_nodes'] and slack(ranks, flow) == 0:
                    part_tree['all_nodes'][direct_node_id] = direct_node
                    part_tree[PE.flows][flow_id] = flow
                    dfs(direct_node)

    for node in list(part_tree['all_nodes'].values()):
        dfs(node)

    return len(list(part_tree['all_nodes'].keys()))


def find_min_slack_flow(part_tree, pipeline, ranks):
    min_slack = max(list(ranks.values())) - min(list(ranks.values()))
    min_slack_flow = None
    for flow_id, flow in pipeline[PE.flows].items():
        if (flow[PE.source] in part_tree['all_nodes']) is not (flow[PE.target] in part_tree['all_nodes']):
            if slack(ranks, flow) < min_slack:
                min_slack = slack(ranks, flow)
                min_slack_flow = flow
    return min_slack_flow


def shift_ranks(ranks, node_ids, delta):
    for node_id in node_ids:
        ranks[node_id] += delta
