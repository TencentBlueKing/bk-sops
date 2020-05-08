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

from pipeline.core.constants import PE
from pipeline.validators.utils import format_to_list

from pipeline_web.drawing_new.constants import MIN_LEN


def longest_path_ranker(pipeline):
    """
    @summary: 按照最长路径算法（所有叶子节点层级一样），快速初始化一种 rank，由于标准运维是一定是以开始节点开始，结束节点结束，所以
        可以尽量让最长路径对齐在开始节点，这样多分支的节点会在前面对齐
    @return:
    @example: A 为结束节点
                             +---+        +---+        +---+
                         --->| B |------->| C |------->| E |
                   -----/    +---+        +---+        +---+
             -----/            -2           -1           0
    +---+---/                             +---+        +---+
    | A |-------------------------------->| D |------->| F |
    +---+-\                               +---+        +---+
     -4    -\                               -1           0
             -\ +---+        +---+        +---+        +---+
               >| G |------->| H |------->| I |------->| J |
                +---+        +---+        +---+        +---+
                  -3           -2           -1           0
    """  # noqa
    ranks = {}

    def dfs(node):
        if node[PE.id] in ranks:
            return ranks[node[PE.id]]

        incoming_node_ranks = []
        for flow_id in format_to_list(node[PE.incoming]):
            flow = pipeline[PE.flows][flow_id]
            incoming_node = pipeline['all_nodes'][flow[PE.source]]
            incoming_node_ranks.append(dfs(incoming_node) - MIN_LEN)

        if not incoming_node_ranks:
            return 0
        else:
            return min(incoming_node_ranks)

    for node_id, node in pipeline['all_nodes'].items():
        ranks[node_id] = dfs(node)

    # 重置结束节点的 rank 为 0，并且其他节点 rank 小于 结束节点
    min_rank = min(list(ranks.values()))
    for key in ranks:
        ranks[key] = min_rank - ranks[key]
    return ranks
