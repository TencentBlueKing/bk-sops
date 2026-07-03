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
import datetime

from django.test import TransactionTestCase
from django.test.utils import override_settings
from fakeredis import FakeRedis
from mock import patch

from gcloud.taskflow3.management.commands.node_timeout_process import Command
from gcloud.taskflow3.models import TimeoutNodesRecord


class NodeTimeoutProcessCommandTestCase(TransactionTestCase):
    def setUp(self):
        self.node_pool = "test_node_pool"
        self.command = Command()
        self.redis_inst = FakeRedis()

    @override_settings(EXECUTING_NODE_POOL="test_node_pool")
    def test_command_simple(self):
        now = datetime.datetime.now().timestamp()
        self.redis_inst.zadd(self.node_pool, mapping={"test": now})
        self.assertEqual(self.redis_inst.zcard(self.node_pool), 1)

        # 使用mock避免实际数据库操作
        with patch.object(TimeoutNodesRecord.objects, "create") as mock_create:
            mock_create.return_value.id = 1  # 模拟返回的record id
            self.command._pop_timeout_nodes(self.redis_inst, self.node_pool)

        self.assertEqual(self.redis_inst.zcard(self.node_pool), 0)
        mock_create.assert_called_once()

    @override_settings(EXECUTING_NODE_POOL="test_node_pool")
    def test_command_complicated(self):
        now = datetime.datetime.now()
        time1 = now.timestamp()
        time2 = (now + datetime.timedelta(minutes=5)).timestamp()
        self.redis_inst.zadd(self.node_pool, mapping={"time1": time1, "time2": time2})
        self.assertEqual(self.redis_inst.zcard(self.node_pool), 2)

        # 使用mock避免实际数据库操作
        with patch.object(TimeoutNodesRecord.objects, "create") as mock_create:
            mock_create.return_value.id = 1  # 模拟返回的record id
            self.command._pop_timeout_nodes(self.redis_inst, self.node_pool)

        self.assertEqual(self.redis_inst.zcard(self.node_pool), 1)
        mock_create.assert_called_once()
