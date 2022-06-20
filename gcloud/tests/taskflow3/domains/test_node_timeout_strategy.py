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
from mock import MagicMock

from django.test import TestCase
from mock.mock import call

from gcloud.taskflow3.domains import node_timeout_strategy
from gcloud.taskflow3.domains.node_timeout_strategy import NodeTimeoutStrategy


class NodeTimeoutStrategyTestCase(TestCase):
    def setUp(self):
        self.handlers = node_timeout_strategy.node_timeout_handler

    def test_forced_fail_strategy(self):
        task = MagicMock()
        task.nodes_action = MagicMock(return_value={"result": True})
        node_id = "node_id"
        handler = self.handlers["forced_fail"]
        result = handler.deal_with_timeout_node(task, node_id)
        self.assertEqual(result, {"result": True})
        task.nodes_action.assert_called_once_with("forced_fail", node_id, NodeTimeoutStrategy.TIMEOUT_NODE_OPERATOR)

    def test_forced_fail_and_skip_strategy_failed(self):
        task = MagicMock()
        task.nodes_action = MagicMock(return_value={"result": False})
        node_id = "node_id"
        handler = self.handlers["forced_fail_and_skip"]
        result = handler.deal_with_timeout_node(task, node_id)
        self.assertEqual(result, {"result": False})
        task.nodes_action.assert_called_once_with("forced_fail", node_id, NodeTimeoutStrategy.TIMEOUT_NODE_OPERATOR)

    def test_forced_fail_and_skip_strategy_success(self):
        task = MagicMock()
        task.nodes_action = MagicMock(return_value={"result": True})
        node_id = "node_id"
        handler = self.handlers["forced_fail_and_skip"]
        result = handler.deal_with_timeout_node(task, node_id)
        self.assertEqual(result, {"result": True})
        self.assertEqual(task.nodes_action.call_count, 2)
        task.nodes_action.assert_has_calls(
            [
                call("forced_fail", node_id, NodeTimeoutStrategy.TIMEOUT_NODE_OPERATOR),
                call("skip", node_id, NodeTimeoutStrategy.TIMEOUT_NODE_OPERATOR),
            ],
        )
