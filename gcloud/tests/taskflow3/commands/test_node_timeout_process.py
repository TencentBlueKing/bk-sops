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

from django.test import TestCase
from django.test.utils import override_settings
from django.conf import settings
from fakeredis import FakeRedis

from gcloud.taskflow3.management.commands.node_timeout_process import Command
from gcloud.taskflow3.models import TimeoutNodesRecord


class NodeTimeoutProcessCommandTestCase(TestCase):
    def setUp(self):
        self.node_pool = "test_node_pool"
        self.command = Command()

    @override_settings(redis_inst=FakeRedis())
    @override_settings(EXECUTING_NODE_POOL="test_node_pool")
    def test_command_simple(self):
        now = datetime.datetime.now().timestamp()
        settings.redis_inst.zadd(self.node_pool, mapping={"test": now})
        self.assertEqual(settings.redis_inst.zcard(self.node_pool), 1)
        self.command._pop_timeout_nodes(settings.redis_inst, self.node_pool)
        self.assertEqual(settings.redis_inst.zcard(self.node_pool), 0)
        self.assertEqual(len(TimeoutNodesRecord.objects.all()), 1)

    @override_settings(redis_inst=FakeRedis())
    @override_settings(EXECUTING_NODE_POOL="test_node_pool")
    def test_command_complicated(self):
        now = datetime.datetime.now()
        time1 = now.timestamp()
        time2 = (now + datetime.timedelta(minutes=5)).timestamp()
        settings.redis_inst.zadd(self.node_pool, mapping={"time1": time1, "time2": time2})
        self.assertEqual(settings.redis_inst.zcard(self.node_pool), 2)
        self.command._pop_timeout_nodes(settings.redis_inst, self.node_pool)
        self.assertEqual(settings.redis_inst.zcard(self.node_pool), 1)
        self.assertEqual(len(TimeoutNodesRecord.objects.all()), 1)
