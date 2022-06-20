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

from mock import patch, MagicMock

from django.test import TestCase

from gcloud.taskflow3.models import AutoRetryNodeStrategy
from gcloud.taskflow3.signals.handlers import _dispatch_auto_retry_node_task


class DispatchAutoRetryNodeTaskTestCase(TestCase):
    def test_strategy_not_exist(self):
        result = _dispatch_auto_retry_node_task("root", "node_id", 2)
        self.assertFalse(result)

    def test_retry_times_exceed(self):
        AutoRetryNodeStrategy.objects.create(
            taskflow_id=1, root_pipeline_id="root", node_id="node_id", retry_times=10, max_retry_times=10
        )

        result = _dispatch_auto_retry_node_task("root", "node_id", 2)
        self.assertFalse(result)

    def test_apply_async_raise(self):
        root_pipeline_id = "root"
        node_id = "node"
        engine_ver = 2
        strategy = AutoRetryNodeStrategy.objects.create(
            taskflow_id=1, root_pipeline_id=root_pipeline_id, node_id=node_id, retry_times=2, max_retry_times=10
        )
        auto_retry_node = MagicMock()
        auto_retry_node.apply_async = MagicMock(side_effect=Exception)

        with patch("gcloud.taskflow3.signals.handlers.auto_retry_node", auto_retry_node):
            result = _dispatch_auto_retry_node_task(root_pipeline_id, node_id, engine_ver)
            self.assertFalse(result)

        auto_retry_node.apply_async.assert_called_once_with(
            kwargs={
                "taskflow_id": strategy.taskflow_id,
                "root_pipeline_id": root_pipeline_id,
                "node_id": node_id,
                "retry_times": strategy.retry_times,
                "engine_ver": engine_ver,
            },
            queue="node_auto_retry",
            routing_key="node_auto_retry",
            countdown=0,
        )

    def test_success(self):
        root_pipeline_id = "root"
        node_id = "node"
        engine_ver = 2
        strategy = AutoRetryNodeStrategy.objects.create(
            taskflow_id=1,
            root_pipeline_id=root_pipeline_id,
            node_id=node_id,
            retry_times=2,
            max_retry_times=10,
            interval=2,
        )
        auto_retry_node = MagicMock()

        with patch("gcloud.taskflow3.signals.handlers.auto_retry_node", auto_retry_node):
            result = _dispatch_auto_retry_node_task(root_pipeline_id, node_id, engine_ver)
            self.assertTrue(result)

        auto_retry_node.apply_async.assert_called_once_with(
            kwargs={
                "taskflow_id": strategy.taskflow_id,
                "root_pipeline_id": root_pipeline_id,
                "node_id": node_id,
                "retry_times": strategy.retry_times,
                "engine_ver": engine_ver,
            },
            queue="node_auto_retry",
            routing_key="node_auto_retry",
            countdown=2,
        )
