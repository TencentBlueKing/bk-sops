# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""


def topology_sort(relations):
    """
    拓扑排序
    :params relations: 拓扑关系字典，需保证输入关系合法
    :type relations: dict, key为引用者id，value为被引用者id列表
    :return 关系拓扑排序后顺序列表
    :rtype list
    """
    visited = set()
    orders = []

    def dfs(referencer_id):
        if referencer_id in visited:
            return
        for referenced_id in relations.get(referencer_id, []):
            dfs(referenced_id)
        visited.add(referencer_id)
        orders.append(referencer_id)

    for rid in relations:
        dfs(rid)

    return orders
