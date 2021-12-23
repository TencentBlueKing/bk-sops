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
from abc import ABCMeta, abstractmethod


class NodeTimeoutStrategy(metaclass=ABCMeta):
    TIMEOUT_NODE_OPERATOR = "sops_system"

    @abstractmethod
    def deal_with_timeout_node(self, task, node_id):
        pass


class ForcedFailStrategy(NodeTimeoutStrategy):
    def deal_with_timeout_node(self, task, node_id):
        return task.nodes_action("forced_fail", node_id, self.TIMEOUT_NODE_OPERATOR)


class ForcedFailAndSkipStrategy(NodeTimeoutStrategy):
    def deal_with_timeout_node(self, task, node_id):
        fail_result = task.nodes_action("forced_fail", node_id, self.TIMEOUT_NODE_OPERATOR)
        if fail_result["result"]:
            skip_result = task.nodes_action("skip", node_id, self.TIMEOUT_NODE_OPERATOR)
            return skip_result
        return fail_result


node_timeout_handler = {
    "forced_fail": ForcedFailStrategy(),
    "forced_fail_and_skip": ForcedFailAndSkipStrategy(),
}
