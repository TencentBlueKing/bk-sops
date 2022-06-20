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
from django.conf import settings
from django.test import TestCase
from fakeredis import FakeRedis
from bamboo_engine import states as bamboo_engine_states

from gcloud.taskflow3.models import TimeoutNodeConfig
from gcloud.taskflow3.signals.handlers import _node_timeout_info_update


class NodeTimeoutInfoUpdateTestCase(TestCase):
    def setUp(self):
        self.node_id = "node_id"
        self.version = "version"
        self.redis_inst = FakeRedis()
        self.time_config = TimeoutNodeConfig.objects.create(
            task_id=1, root_pipeline_id="root_pipeline_id", action="forced_fail", node_id=self.node_id, timeout=5
        )

    def test__node_timeout_info_update_running_state(self):
        to_state = bamboo_engine_states.RUNNING
        _node_timeout_info_update(self.redis_inst, to_state, self.node_id, self.version)
        self.assertEqual(self.redis_inst.zcard(settings.EXECUTING_NODE_POOL), 1)
        another_version = "version2"
        _node_timeout_info_update(self.redis_inst, to_state, self.node_id, another_version)
        self.assertEqual(self.redis_inst.zcard(settings.EXECUTING_NODE_POOL), 2)

    def test__node_timeout_info_update_finish_state(self):
        to_state = bamboo_engine_states.RUNNING
        _node_timeout_info_update(self.redis_inst, to_state, self.node_id, self.version)
        to_state = bamboo_engine_states.FINISHED
        _node_timeout_info_update(self.redis_inst, to_state, self.node_id, self.version)
        self.assertEqual(self.redis_inst.zcard(settings.EXECUTING_NODE_POOL), 0)

    def test__node_timeout_info_update_fail_state(self):
        to_state = bamboo_engine_states.RUNNING
        _node_timeout_info_update(self.redis_inst, to_state, self.node_id, self.version)
        to_state = bamboo_engine_states.FAILED
        _node_timeout_info_update(self.redis_inst, to_state, self.node_id, self.version)
        self.assertEqual(self.redis_inst.zcard(settings.EXECUTING_NODE_POOL), 0)
