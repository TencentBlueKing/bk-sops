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


class Graph(object):
    def __init__(self, nodes, flows):
        self.nodes = nodes
        self.flows = flows
        self.path = []
        self.last_visited_node = ''

    def has_cycle(self):
        self.path = []
        for node in self.nodes:
            if self.visit(node):
                return True
        return False

    def visit(self, node):
        self.path.append(node)
        target_nodes = [flow[1] for flow in self.flows if flow[0] == node]
        for target in target_nodes:
            if target in self.path:
                self.last_visited_node = target
                return True
            if self.visit(target):
                return True
        self.path.remove(node)
        return False

    def get_cycle(self):
        if self.has_cycle():
            index = self.path.index(self.last_visited_node)
            cycle = self.path[index:]
            cycle.append(self.last_visited_node)
            return cycle
        return []


if __name__ == '__main__':
    graph1 = Graph([1, 2, 3, 4], [[1, 2], [2, 3], [3, 4]])
    print graph1.has_cycle(), graph1.get_cycle()
    graph2 = Graph([1, 2, 3, 4], [[1, 2], [2, 3], [3, 4], [4, 1]])
    print graph2.has_cycle(), graph2.get_cycle()
    graph3 = Graph([1, 2, 3, 4], [[1, 2], [2, 3], [3, 4], [4, 2]])
    print graph3.has_cycle(), graph3.get_cycle()
