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
import json
from mock import patch, MagicMock, call

from django.test import TestCase
from pipeline.eri.models import Process, State

from gcloud.taskflow3.celery.tasks import dispatch_timeout_nodes, execute_node_timeout_strategy
from gcloud.taskflow3.models import TimeoutNodeConfig, TimeoutNodesRecord


class NodeTimeoutTaskTestCase(TestCase):
    def setUp(self):
        self.node_id = "node_id"
        self.version = "version"
        self.action = "forced_fail"
        self.root_pipeline_id = "root_pipeline_id"

    def test_dispatch_timeout_nodes(self):
        mock_node_timeout_executor = MagicMock()
        mock_node_timeout_executor.apply_async = MagicMock()
        with patch("gcloud.taskflow3.celery.tasks.execute_node_timeout_strategy", mock_node_timeout_executor):
            TimeoutNodesRecord.objects.create(id=1, timeout_nodes=json.dumps(["node1_version1", "node2_version2"]))
            dispatch_timeout_nodes(record_id=1)
            mock_node_timeout_executor.apply_async.assert_has_calls(
                [
                    call(
                        kwargs={"node_id": "node1", "version": "version1"},
                        queue="timeout_node_execute",
                        routing_key="timeout_node_execute",
                    ),
                    call(
                        kwargs={"node_id": "node2", "version": "version2"},
                        queue="timeout_node_execute",
                        routing_key="timeout_node_execute",
                    ),
                ]
            )

    @patch("gcloud.taskflow3.celery.tasks.TaskFlowInstance.objects.get", MagicMock(return_value=None))
    def test_execute_node_timeout_strategy_success(self):
        TimeoutNodeConfig.objects.create(
            task_id=1, root_pipeline_id=self.root_pipeline_id, action=self.action, node_id=self.node_id, timeout=30
        )
        Process.objects.create(root_pipeline_id=self.root_pipeline_id, current_node_id=self.node_id, priority=1)
        State.objects.create(node_id=self.node_id, name="name", version=self.version)
        mock_handler = MagicMock()
        mock_handler.deal_with_timeout_node = MagicMock(return_value=True)
        with patch("gcloud.taskflow3.celery.tasks.node_timeout_handler", {self.action: mock_handler}):
            result = execute_node_timeout_strategy(self.node_id, self.version)
            self.assertEqual(result, True)
            mock_handler.deal_with_timeout_node.assert_called_once_with(None, self.node_id)

    @patch("gcloud.taskflow3.celery.tasks.TaskFlowInstance.objects.get", MagicMock(return_value=None))
    def test_execute_node_timeout_strategy_not_current_node(self):
        TimeoutNodeConfig.objects.create(
            task_id=1, root_pipeline_id=self.root_pipeline_id, action=self.action, node_id=self.node_id, timeout=30
        )
        Process.objects.create(root_pipeline_id=self.root_pipeline_id, current_node_id="next_node", priority=1)
        State.objects.create(node_id=self.node_id, name="name", version=self.version)
        mock_handler = MagicMock()
        mock_handler.deal_with_timeout_node = MagicMock(return_value=True)
        with patch("gcloud.taskflow3.celery.tasks.node_timeout_handler", {self.action: mock_handler}):
            result = execute_node_timeout_strategy(self.node_id, self.version)
            self.assertEqual(result["result"], False)
            mock_handler.deal_with_timeout_node.assert_not_called()

    @patch("gcloud.taskflow3.celery.tasks.TaskFlowInstance.objects.get", MagicMock(return_value=None))
    def test_execute_node_timeout_strategy_not_current_version(self):
        TimeoutNodeConfig.objects.create(
            task_id=1, root_pipeline_id=self.root_pipeline_id, action=self.action, node_id=self.node_id, timeout=30
        )
        Process.objects.create(root_pipeline_id=self.root_pipeline_id, current_node_id=self.node_id, priority=1)
        State.objects.create(node_id=self.node_id, name="name", version="ano_version")
        mock_handler = MagicMock()
        mock_handler.deal_with_timeout_node = MagicMock(return_value=True)
        with patch("gcloud.taskflow3.celery.tasks.node_timeout_handler", {self.action: mock_handler}):
            result = execute_node_timeout_strategy(self.node_id, self.version)
            self.assertEqual(result["result"], False)
            mock_handler.deal_with_timeout_node.assert_not_called()
