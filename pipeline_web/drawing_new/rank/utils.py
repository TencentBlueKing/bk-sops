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
from pipeline_web.drawing_new.constants import MIN_LEN


def max_rank(ranks):
    return max(list(ranks.values()))


def min_rank(ranks):
    return min(list(ranks.values()))


def normalize_ranks(ranks):
    """
    @summary: Adjusts the ranks for all nodes in the graph such that all nodes v have rank(v) >= 0
        and at least one node w has rank(w) = 0.
    @param ranks:
    @return:
    """
    min_rk = min_rank(ranks)
    for node_id in ranks:
        ranks[node_id] -= min_rk


def slack(ranks, flow):
    """
    @summary: Returns the amount of slack for the given flow. The slack is defined as the
        difference between the length of the flow and its minimum length.
        松弛度被定义为其长度和最小长度之间的差值，边的松弛度为0，则为紧凑的。
    @param ranks:
    @param flow:
    @return:
    """
    return ranks[flow[PE.target]] - ranks[flow[PE.source]] - MIN_LEN
